from ..views import *


class CreateOrderAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:

            user = request.user

            shipping_address_id = request.data.get(
                "shipping_address_id"
            )

            payment_method = request.data.get(
                "payment_method"
            )

            VALID_PAYMENT_METHODS = [
                "COD",
                "STRIPE"
            ]

            # =====================================================
            # VALIDATION
            # =====================================================

            if not shipping_address_id:

                return Response(
                    {
                        "status": "fail",
                        "message": (
                            "shipping_address_id required"
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            if payment_method not in VALID_PAYMENT_METHODS:

                return Response(
                    {
                        "status": "fail",
                        "message": (
                            "Invalid payment method"
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            shipping_address = (
                Address.objects.filter(
                    id=shipping_address_id,
                    user=user,
                    is_deleted=False
                ).first()
            )

            if not shipping_address:

                return Response(
                    {
                        "status": "fail",
                        "message": (
                            "Shipping address not found"
                        )
                    },
                    status=status.HTTP_404_NOT_FOUND
                )

            cart = (
                Cart.objects.filter(
                    user=user,
                    is_deleted=False
                ).first()
            )

            if not cart:

                return Response(
                    {
                        "status": "fail",
                        "message": "Cart not found"
                    },
                    status=status.HTTP_404_NOT_FOUND
                )

            cart_items = (
                CartItem.objects
                .select_related("product")
                .filter(
                    cart=cart,
                    is_deleted=False
                )
            )

            if not cart_items.exists():

                return Response(
                    {
                        "status": "fail",
                        "message": "Cart is empty"
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            subtotal = Decimal("0.00")

            total_discount = Decimal("0.00")

            total_saved_amount = Decimal("0.00")

            shipping_charge = Decimal("0.00")

            tax_amount = Decimal("0.00")

            ordered_products = []

            stripe_data = None

            # =====================================================
            # TRANSACTION START
            # =====================================================

            with transaction.atomic():

                locked_cart_items = (
                    cart_items.select_for_update()
                )

                # =================================================
                # PRODUCT VALIDATION + PRICE CALCULATION
                # =================================================

                for item in locked_cart_items:

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

                        return Response(
                            {
                                "status": "fail",
                                "message": (
                                    f"{item.product.name} unavailable"
                                )
                            },
                            status=status.HTTP_400_BAD_REQUEST
                        )

                    if product.stock < item.quantity:

                        return Response(
                            {
                                "status": "fail",
                                "message": (
                                    f"Only "
                                    f"{product.stock} stock "
                                    f"left for "
                                    f"{product.name}"
                                )
                            },
                            status=status.HTTP_400_BAD_REQUEST
                        )

                    mrp = Decimal(
                        str(product.price)
                    )

                    discount_percentage = Decimal(
                        str(
                            product.discount_percentage or 0
                        )
                    )

                    discount_amount = (
                        mrp * discount_percentage
                    ) / Decimal("100")

                    selling_price = (
                        mrp - discount_amount
                    )

                    item_total = (
                        selling_price * item.quantity
                    )

                    saved_amount = (
                        discount_amount * item.quantity
                    )

                    subtotal += item_total

                    total_discount += saved_amount

                    total_saved_amount += saved_amount

                # =================================================
                # SHIPPING CHARGE
                # =================================================

                shipping_charge = (
                    Decimal("0.00")
                    if subtotal >= Decimal("500")
                    else Decimal("100.00")
                )

                # =================================================
                # GST TAX
                # =================================================

                tax_amount = (
                    subtotal * Decimal("18")
                ) / Decimal("100")

                # =================================================
                # TOTAL AMOUNT
                # =================================================

                total_amount = (
                    subtotal +
                    shipping_charge +
                    tax_amount
                )

                if total_amount < 0:

                    total_amount = Decimal("0.00")

                # =================================================
                # CREATE ORDER
                # =================================================

                order = Order.objects.create(

                    user=user,

                    shipping_name=(
                        shipping_address.contact_name
                    ),

                    shipping_email=user.email,

                    shipping_phone=(
                        shipping_address.contact_no
                    ),

                    shipping_address_line1=(
                        f"{shipping_address.house_no}, "
                        f"{shipping_address.area_street}"
                    ),

                    shipping_address_line2=(
                        shipping_address.locality
                    ),

                    shipping_city=(
                        shipping_address.city
                    ),

                    shipping_state=(
                        shipping_address.state
                    ),

                    shipping_pincode=(
                        shipping_address.pincode
                    ),

                    shipping_country=(
                        shipping_address.country
                    ),

                    subtotal=subtotal,

                    discount_amount=(
                        total_discount
                    ),

                    shipping_charge=(
                        shipping_charge
                    ),

                    tax_amount=tax_amount,

                    total_amount=(
                        total_amount
                    ),

                    payment_method=(
                        "COD"
                        if payment_method == "COD"
                        else "CARD"
                    ),

                    payment_status=(
                        "COD"
                        if payment_method == "COD"
                        else "PENDING"
                    ),

                    status=(
                        "CONFIRMED"
                        if payment_method == "COD"
                        else "PENDING"
                    ),

                    confirmed_at=(
                        timezone.now()
                    ) if payment_method == "COD"
                    else None,

                    created_by=user
                )

                # =================================================
                # CREATE ORDER ITEMS
                # =================================================

                for item in locked_cart_items:

                    product = item.product

                    mrp = Decimal(
                        str(product.price)
                    )

                    discount_percentage = Decimal(
                        str(
                            product.discount_percentage or 0
                        )
                    )

                    discount_amount = (
                        mrp * discount_percentage
                    ) / Decimal("100")

                    selling_price = (
                        mrp - discount_amount
                    )

                    item_total = (
                        selling_price * item.quantity
                    )

                    image = (
                        product.product_image.first()
                    )

                    image_url = (
                        request.build_absolute_uri(
                            image.image.url
                        )
                        if image else None
                    )

                    order_item = (
                        OrderItem.objects.create(

                            order=order,

                            product=product,

                            product_name=product.name,

                            product_image=image_url,

                            product_price=selling_price,

                            original_price=mrp,

                            discount_percentage=int(
                                discount_percentage
                            ),

                            quantity=item.quantity,

                            size=getattr(
                                item,
                                "size",
                                None
                            ),

                            color=getattr(
                                item,
                                "color",
                                None
                            )
                        )
                    )

                    ordered_products.append({

                        "order_item_id": (
                            order_item.id
                        ),

                        "product_id": (
                            product.id
                        ),

                        "product_name": (
                            product.name
                        ),

                        "product_image": (
                            image_url
                        ),

                        "quantity": (
                            item.quantity
                        ),

                        "size": getattr(
                            item,
                            "size",
                            None
                        ),

                        "color": getattr(
                            item,
                            "color",
                            None
                        ),

                        "price_details": {

                            "mrp": float(mrp),

                            "selling_price": float(
                                selling_price
                            ),

                            "discount_percentage": float(
                                discount_percentage
                            ),

                            "saved_amount": float(
                                discount_amount *
                                item.quantity
                            )
                        },

                        "item_total": float(
                            item_total
                        )
                    })

                # =================================================
                # COD FLOW
                # =================================================

                if payment_method == "COD":

                    for item in locked_cart_items:

                        updated_rows = (
                            Product.objects.filter(
                                id=item.product.id,
                                stock__gte=item.quantity
                            ).update(
                                stock=F("stock") - item.quantity
                            )
                        )

                        if updated_rows == 0:

                            raise Exception(
                                f"Insufficient stock for "
                                f"{item.product.name}"
                            )

                    locked_cart_items.update(
                        is_deleted=True
                    )

                    add_tracking_entry(
                        order,
                        "CONFIRMED",
                        "COD Order Confirmed"
                    )

                    # =============================================
                    # WHATSAPP MESSAGE
                    # =============================================

                    whatsapp_message = (

                        f"Your order has been placed successfully.\n\n"

                        f"Order ID : "
                        f"{order.order_id}\n"

                        f"Customer Name : "
                        f"{shipping_address.contact_name}\n"

                        f"Mobile Number : "
                        f"{shipping_address.contact_no}\n"

                        f"Address : "
                        f"{shipping_address.house_no}, "
                        f"{shipping_address.area_street}, "
                        f"{shipping_address.city}\n\n"

                        f"Total Amount : ₹"
                        f"{total_amount}\n"

                        f"Payment Method : COD\n\n"

                        f"Thank you for shopping with us."
                    )

                    send_whatsapp_message(
                        mobile=(
                            shipping_address.contact_no
                        ),
                        message=whatsapp_message
                    )

                # =================================================
                # STRIPE FLOW
                # =================================================

                else:

                    frontend_url = getattr(
                        settings,
                        "FRONTEND_URL",
                        "http://localhost:3000"
                    )

                    checkout_session = (
                        stripe.checkout.Session.create(

                            payment_method_types=[
                                "card"
                            ],

                            mode="payment",

                            customer_email=user.email,

                            success_url=(
                                f"{frontend_url}"
                                f"/payment-success?"
                                f"order_id="
                                f"{order.order_id}"
                            ),

                            cancel_url=(
                                f"{frontend_url}"
                                f"/payment-failed?"
                                f"order_id="
                                f"{order.order_id}"
                            ),

                            metadata={

                                "order_id": str(
                                    order.order_id
                                ),

                                "user_id": str(
                                    user.id
                                )
                            },

                            line_items=[

                                {
                                    "price_data": {

                                        "currency": "inr",

                                        "product_data": {

                                            "name": (
                                                f"Order "
                                                f"{order.order_id}"
                                            )
                                        },

                                        "unit_amount": int(
                                            total_amount * 100
                                        )
                                    },

                                    "quantity": 1
                                }
                            ]
                        )
                    )

                    order.payment_id = (
                        checkout_session.payment_intent
                    )

                    order.payment_response = (
                        checkout_session.to_dict()
                    )

                    order.save(
                        update_fields=[
                            "payment_id",
                            "payment_response"
                        ]
                    )

                    stripe_data = {

                        "checkout_url": (
                            checkout_session.url
                        ),

                        "session_id": (
                            checkout_session.id
                        ),

                        "publishable_key": (
                            settings
                            .STRIPE_PUBLISHABLE_KEY
                        )
                    }

                # =================================================
                # ADMIN NOTIFICATION
                # =================================================

                Notify_Admin.objects.create(

                    title="New Order Received",

                    message=(

                        f"New order received from "

                        f"{shipping_address.contact_name} "

                        f"| Order ID : "

                        f"{order.order_id} "

                        f"| Amount : ₹{total_amount}"
                    ),

                    order=order
                )

            # =====================================================
            # RESPONSE
            # =====================================================

            return Response(

                {
                    "status": "success",

                    "message": (

                        "Order placed successfully"
                        if payment_method == "COD"
                        else (
                            "Redirect user to Stripe payment page"
                        )
                    ),

                    "data": {

                        # =========================================
                        # USER DETAILS
                        # =========================================

                        "customer_details": {

                            "user_id": user.id,

                            "full_name": (
                                f"{user.first_name} "
                                f"{user.last_name}"
                            ).strip(),

                            "email": user.email,

                            "mobile_number": (
                                shipping_address.contact_no
                            )
                        },

                        # =========================================
                        # SHIPPING ADDRESS
                        # =========================================

                        "shipping_address": {

                            "name": (
                                shipping_address.contact_name
                            ),

                            "mobile_number": (
                                shipping_address.contact_no
                            ),

                            "address_line_1": (
                                f"{shipping_address.house_no}, "
                                f"{shipping_address.area_street}"
                            ),

                            "address_line_2": (
                                shipping_address.locality
                            ),

                            "city": (
                                shipping_address.city
                            ),

                            "state": (
                                shipping_address.state
                            ),

                            "pincode": (
                                shipping_address.pincode
                            ),

                            "country": (
                                shipping_address.country
                            )
                        },

                        # =========================================
                        # ORDER DETAILS
                        # =========================================

                        "order_details": {

                            "order_id": (
                                order.order_id
                            ),

                            "payment_method": (
                                order.payment_method
                            ),

                            "payment_status": (
                                order.payment_status
                            ),

                            "order_status": (
                                order.status
                            ),

                            "expected_delivery_date": (

                                timezone.now() +
                                timedelta(days=5)

                            ).date()
                        },

                        # =========================================
                        # PRICE DETAILS
                        # =========================================

                        "price_details": {

                            "subtotal": float(
                                subtotal
                            ),

                            "product_discount": float(
                                total_discount
                            ),

                            "shipping_charge": float(
                                shipping_charge
                            ),

                            "tax_amount": float(
                                tax_amount
                            ),

                            "total_amount": float(
                                total_amount
                            ),

                            "total_saved_amount": float(
                                total_saved_amount
                            )
                        },

                        # =========================================
                        # ORDER PRODUCTS
                        # =========================================

                        "ordered_products": (
                            ordered_products
                        ),

                        # =========================================
                        # PAYMENT GATEWAY
                        # =========================================

                        "payment_gateway": (
                            stripe_data
                        )
                    }
                },

                status=status.HTTP_201_CREATED
            )

        except Exception as e:

            return Response(
                {
                    "status": "error",
                    "message": str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class CancelOrderAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        try:
            order_id = request.query_params.get('order_id')
            reason = request.data.get("reason", "User cancelled")

            missing = check_missing_fields(request.data, ["order_id"])
            if missing:
                return missing

            int_error = integer_field_validator(request, ["order_id"])
            if int_error:
                return int_error

            order = Order.objects.filter(order_id=order_id,user=request.user,is_deleted=False).first()
            if not order:
                return Response({"status": "fail","message": f"{NOT_FOUND} - Order not found"}, 
                                status=status.HTTP_404_NOT_FOUND)

            if not order.can_cancel:
                return Response({"status": "fail","message": f"{BAD_REQUEST} - Order cannot be cancelled"}, 
                                status=status.HTTP_400_BAD_REQUEST)

            with transaction.atomic():
                for item in order.items.select_related("product").all():
                    product = item.product
                    product.stock = F("stock") + item.quantity
                    product.save(update_fields=["stock"])

                update_order_status(order,"CANCELLED",description=reason)
                order.refresh_from_db()

            response_data = {
                "status": "success",
                "message": f"{SUCCESS} - Order cancelled successfully",
                "data": {
                    "order_id": order.order_id,
                    "status": order.status
                }
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"status": "error","message": f"{INTERNAL_SERVER_ERROR} - Internal Server Error : {str(e)}"}, 
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)