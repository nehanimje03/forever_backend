import stripe

from django.conf import settings
from django.db import transaction
from django.db.models import F
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone

from orders.models import Notify_Admin, Order, OrderItem
from products.models import CartItem, Product
from utils.api.core_utils import send_whatsapp_message
from utils.api.order_utils import add_tracking_entry

stripe.api_key = settings.STRIPE_SECRET_KEY


@csrf_exempt
def stripe_webhook(request):

    payload = request.body

    sig_header = request.META.get(
        "HTTP_STRIPE_SIGNATURE"
    )

    endpoint_secret = (
        settings.STRIPE_WEBHOOK_SECRET
    )

    try:

        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            endpoint_secret
        )

    except ValueError:

        return HttpResponse(status=400)

    except stripe.error.SignatureVerificationError:

        return HttpResponse(status=400)

    # =====================================================
    # PAYMENT SUCCESS
    # =====================================================

    if event["type"] == "checkout.session.completed":

        session = event["data"]["object"]

        order_id = session["metadata"].get(
            "order_id"
        )

        payment_intent = session.get(
            "payment_intent"
        )

        with transaction.atomic():

            order = (
                Order.objects
                .select_for_update()
                .filter(order_id=order_id)
                .first()
            )

            if not order:

                return HttpResponse(status=404)

            # ==========================================
            # DUPLICATE WEBHOOK PROTECTION
            # ==========================================

            if order.payment_status == "PAID":

                return HttpResponse(status=200)

            order_items = (
                OrderItem.objects
                .select_related("product")
                .filter(order=order)
            )

            # ==========================================
            # STOCK CHECK
            # ==========================================

            for item in order_items:

                product = (
                    Product.objects
                    .select_for_update()
                    .filter(
                        id=item.product.id,
                        is_deleted=False,
                        is_deactive=False
                    )
                    .first()
                )

                if not product:

                    order.payment_status = "FAILED"

                    order.status = "CANCELLED"

                    order.admin_notes = (
                        f"{item.product_name} unavailable"
                    )

                    order.save(
                        update_fields=[
                            "payment_status",
                            "status",
                            "admin_notes",
                            "updated_at"
                        ]
                    )

                    return HttpResponse(status=200)

                if product.stock < item.quantity:

                    order.payment_status = "FAILED"

                    order.status = "CANCELLED"

                    order.admin_notes = (
                        f"Insufficient stock for "
                        f"{product.name}"
                    )

                    order.save(
                        update_fields=[
                            "payment_status",
                            "status",
                            "admin_notes",
                            "updated_at"
                        ]
                    )

                    return HttpResponse(status=200)

            # ==========================================
            # STOCK REDUCE
            # ==========================================

            for item in order_items:

                updated_rows = (
                    Product.objects.filter(
                        id=item.product.id,
                        stock__gte=item.quantity
                    ).update(
                        stock=F("stock") - item.quantity
                    )
                )

                if updated_rows == 0:

                    order.payment_status = "FAILED"

                    order.status = "CANCELLED"

                    order.admin_notes = (
                        "Stock update failed"
                    )

                    order.save(
                        update_fields=[
                            "payment_status",
                            "status",
                            "admin_notes",
                            "updated_at"
                        ]
                    )

                    return HttpResponse(status=200)

            # ==========================================
            # CLEAR CART
            # ==========================================

            CartItem.objects.filter(
                cart__user=order.user,
                is_deleted=False
            ).update(
                is_deleted=True
            )

            # ==========================================
            # PAYMENT SUCCESS UPDATE
            # ==========================================

            order.payment_status = "PAID"

            order.status = "CONFIRMED"

            order.payment_id = payment_intent

            order.payment_response = session.to_dict()

            order.confirmed_at = timezone.now()

            order.updated_at = timezone.now()

            order.save(
                update_fields=[
                    "payment_status",
                    "status",
                    "payment_id",
                    "payment_response",
                    "confirmed_at",
                    "updated_at"
                ]
            )

            # ==========================================
            # ORDER TRACKING
            # ==========================================

            add_tracking_entry(
                order,
                "CONFIRMED",
                "Payment successful and order confirmed"
            )

            # ==========================================
            # WHATSAPP NOTIFICATION
            # ==========================================

            whatsapp_message = (
                f"Payment successful.\n\n"
                f"Order ID : {order.order_id}\n"
                f"Amount : ₹{order.total_amount}\n\n"
                f"Your order is confirmed."
            )

            send_whatsapp_message(
                mobile=order.shipping_phone,
                message=whatsapp_message
            )

            # ==========================================
            # ADMIN NOTIFICATION
            # ==========================================

            Notify_Admin.objects.create(

                title="Payment Successful",

                message=(
                    f"Payment received for "
                    f"Order ID {order.order_id}"
                ),

                order=order
            )

    # =====================================================
    # PAYMENT EXPIRED
    # =====================================================

    elif event["type"] == "checkout.session.expired":

        session = event["data"]["object"]

        order_id = session["metadata"].get(
            "order_id"
        )

        order = (
            Order.objects.filter(
                order_id=order_id
            ).first()
        )

        if order and order.payment_status != "PAID":

            order.payment_status = "FAILED"

            order.status = "CANCELLED"

            order.admin_notes = (
                "Payment session expired"
            )

            order.save(
                update_fields=[
                    "payment_status",
                    "status",
                    "admin_notes",
                    "updated_at"
                ]
            )

            add_tracking_entry(
                order,
                "CANCELLED",
                "Payment session expired"
            )

    # =====================================================
    # PAYMENT FAILED
    # =====================================================

    elif event["type"] == "payment_intent.payment_failed":

        payment_intent = (
            event["data"]["object"]
        )

        order = (
            Order.objects.filter(
                payment_id=payment_intent["id"]
            ).first()
        )

        if order:

            order.payment_status = "FAILED"

            order.status = "CANCELLED"

            order.admin_notes = (
                "Stripe payment failed"
            )

            order.save(
                update_fields=[
                    "payment_status",
                    "status",
                    "admin_notes",
                    "updated_at"
                ]
            )

            add_tracking_entry(
                order,
                "CANCELLED",
                "Payment failed"
            )

    return HttpResponse(status=200)