from ..views import *


class CreateOrderAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            shipping_address_id = request.data.get("shipping_address_id")
            payment_method = request.data.get("payment_method")
            coupon_code = request.data.get("coupon_code")

            required_fields = [
                "shipping_address_id",
                "payment_method"
            ]

            missing = check_missing_fields(
                request.data,
                required_fields
            )

            if missing:
                return missing

            # -----------------------------------
            # VALIDATE PAYMENT METHOD
            # -----------------------------------

            if payment_method not in ["COD", "ONLINE"]:
                return Response(
                    {
                        "status": "fail",
                        "message": f"{BAD_REQUEST} - Invalid payment method"
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            order_items_response = []
            total_saved_amount = Decimal("0.00")

            with transaction.atomic():

                # -----------------------------------
                # GET CART
                # -----------------------------------

                cart = (
                    Cart.objects
                    .select_for_update()
                    .filter(
                        user=request.user,
                        is_deleted=False
                    )
                    .first()
                )

                if not cart:
                    return Response(
                        {
                            "status": "fail",
                            "message": f"{NOT_FOUND} - Cart not found"
                        },
                        status=status.HTTP_404_NOT_FOUND
                    )

                # -----------------------------------
                # GET CART ITEMS
                # -----------------------------------

                cart_items = (
                    CartItem.objects
                    .select_related("product")
                    .select_for_update()
                    .filter(
                        cart=cart,
                        is_deleted=False
                    )
                )

                if not cart_items.exists():
                    return Response(
                        {
                            "status": "fail",
                            "message": f"{BAD_REQUEST} - Cart is empty"
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )

                # -----------------------------------
                # GET SHIPPING ADDRESS
                # -----------------------------------

                shipping_address = (
                    Address.objects
                    .filter(
                        id=shipping_address_id,
                        user=request.user,
                        is_deleted=False
                    )
                    .first()
                )

                if not shipping_address:
                    return Response(
                        {
                            "status": "fail",
                            "message": f"{NOT_FOUND} - Shipping address not found"
                        },
                        status=status.HTTP_404_NOT_FOUND
                    )

                # -----------------------------------
                # CHECK PRODUCT STOCK
                # -----------------------------------

                for item in cart_items:

                    product = (
                        Product.objects
                        .select_for_update()
                        .get(id=item.product.id)
                    )

                    if product.is_deleted or product.is_deactive:
                        return Response(
                            {
                                "status": "fail",
                                "message": f"{BAD_REQUEST} - {product.name} unavailable"
                            },
                            status=status.HTTP_400_BAD_REQUEST
                        )

                    if product.stock < item.quantity:
                        return Response(
                            {
                                "status": "fail",
                                "message": f"{BAD_REQUEST} - Only {product.stock} stock left for {product.name}"
                            },
                            status=status.HTTP_400_BAD_REQUEST
                        )

                # -----------------------------------
                # CALCULATE SUBTOTAL
                # -----------------------------------

                subtotal = Decimal("0.00")

                for item in cart_items:

                    product = item.product

                    mrp = Decimal(str(product.price))

                    discount_percentage = Decimal(
                        str(product.discount_percentage or 0)
                    )

                    discount_amount = (
                        mrp * discount_percentage
                    ) / Decimal("100")

                    deal_price = mrp - discount_amount

                    subtotal += deal_price * item.quantity

                # -----------------------------------
                # SHIPPING CHARGE LOGIC
                # -----------------------------------

                shipping_charge = (
                    Decimal("0.00")
                    if subtotal > Decimal("500")
                    else Decimal("100.00")
                )

                # -----------------------------------
                # ORDER SUMMARY
                # -----------------------------------

                summary = calculate_order_summary(
                    cart_items,
                    coupon_code=coupon_code,
                    shipping_charge=shipping_charge
                )

                # -----------------------------------
                # CREATE ORDER
                # -----------------------------------

                order = Order.objects.create(
                    user=request.user,

                    shipping_name=shipping_address.contact_name,
                    shipping_phone=shipping_address.contact_no,

shipping_address_line1=f"{shipping_address.house_no}, {shipping_address.area_street}",

shipping_address_line2=shipping_address.locality,                    shipping_city=shipping_address.city,
                    shipping_state=shipping_address.state,
                    shipping_pincode=shipping_address.pincode,

                    subtotal=summary["subtotal"],
                    discount_amount=summary["discount_amount"],
                    coupon_code=summary["coupon_code"],
                    coupon_discount=summary["coupon_discount"],
                    shipping_charge=summary["shipping_charge"],
                    tax_amount=summary["tax_amount"],
                    total_amount=summary["total_amount"],

                    payment_method=payment_method,
                    payment_status="PENDING",
                    status="PENDING",

                    created_by=request.user
                )

                # -----------------------------------
                # CREATE ORDER ITEMS
                # -----------------------------------

                for item in cart_items:

                    product = (
                        Product.objects
                        .select_for_update()
                        .get(id=item.product.id)
                    )

                    mrp = Decimal(str(product.price))

                    discount_percentage = Decimal(
                        str(product.discount_percentage or 0)
                    )

                    discount_amount = (
                        mrp * discount_percentage
                    ) / Decimal("100")

                    deal_price = mrp - discount_amount

                    item_total = deal_price * item.quantity

                    saved_amount = (
                        discount_amount * item.quantity
                    )

                    total_saved_amount += saved_amount

                    order_item = OrderItem.objects.create(
                        order=order,
                        product=product,
                        product_name=product.name,
                        product_price=deal_price,
                        quantity=item.quantity,
                        size=item.size if hasattr(item, "size") else None
                    )

                    # STOCK REDUCE
                    product.stock = F("stock") - item.quantity

                    product.save(update_fields=["stock"])

                    image = product.product_image.first()

                    image_url = (
                        request.build_absolute_uri(image.image.url)
                        if image else None
                    )

                    order_items_response.append(
                        {
                            "product_id": product.id,
                            "product_name": product.name,
                            "product_image": image_url,
                            "quantity": item.quantity,
                            "size": getattr(item, "size", None),
                            "price": float(deal_price),
                            "total_amount": float(item_total)
                        }
                    )

                # -----------------------------------
                # CLEAR CART
                # -----------------------------------

                cart_items.update(is_deleted=True)

                # -----------------------------------
                # TRACKING ENTRY
                # -----------------------------------

                add_tracking_entry(
                    order,
                    "PENDING",
                    "Order placed successfully"
                )

                # -----------------------------------
                # RAZORPAY PAYMENT ORDER
                # -----------------------------------

                razorpay_order_data = None

                if payment_method == "ONLINE":

                    client = razorpay.Client(
                        auth=(
                            settings.RAZORPAY_KEY_ID,
                            settings.RAZORPAY_KEY_SECRET
                        )
                    )

                    razorpay_payment = client.order.create(
                        {
                            "amount": int(order.total_amount * 100),
                            "currency": "INR",
                            "receipt": str(order.order_id),
                            "payment_capture": 1
                        }
                    )

                    order.razorpay_order_id = razorpay_payment["id"]

                    order.save(update_fields=["razorpay_order_id"])

                    razorpay_order_data = {
                        "razorpay_order_id": razorpay_payment["id"],
                        "razorpay_key": settings.RAZORPAY_KEY_ID,
                        "amount": razorpay_payment["amount"],
                        "currency": razorpay_payment["currency"]
                    }

                # -----------------------------------
                # WHATSAPP MESSAGE TO USER
                # -----------------------------------

                whatsapp_message = f"""
Your order has been placed successfully.

Order ID : {order.order_id}

Total Amount : ₹{order.total_amount}

Products :
"""

                for item in order_items_response:
                    whatsapp_message += f"""
Product : {item['product_name']}
Qty : {item['quantity']}
Price : ₹{item['price']}
"""

                whatsapp_message += f"""

Thank you for shopping with us.
"""

                # -----------------------------------
                # SEND WHATSAPP MESSAGE
                # -----------------------------------
                # Integrate Twilio / Interakt / Gupshup here

                send_whatsapp_message(
                    mobile=shipping_address.contact_no,
                    message=whatsapp_message
                )
                print(settings.TWILIO_WHATSAPP_NUMBER)

                # -----------------------------------
                # CLIENT / ADMIN NOTIFICATION
                # -----------------------------------

                Notify_Admin.objects.create(
                    title="New Order Received",
                    message=f"New order received - {order.order_id}",
                    order=order
                )

            # -----------------------------------
            # RESPONSE
            # -----------------------------------

            response_data = {
                "status": "success",
                "message": "Order placed successfully",
                "data": {

                    # ---------------------------
                    # USER DETAILS
                    # ---------------------------

                    "user_details": {
                        "name": shipping_address.contact_name,
                        "mobile_number": shipping_address.contact_no,
                        "address": {
"address_line_1": f"{shipping_address.house_no}, {shipping_address.area_street}",

"address_line_2": shipping_address.locality,
                            "city": shipping_address.city,
                            "state": shipping_address.state,
                            "pincode": shipping_address.pincode
                        }
                    },

                    # ---------------------------
                    # ORDER INFO
                    # ---------------------------

                    "order_info": {
                        "order_id": order.order_id,
                        "status": order.status,
                        "payment_method": order.payment_method,
                        "payment_status": order.payment_status,
                        "expected_delivery": (
                            timezone.now() + timedelta(days=5)
                        ).date()
                    },

                    # ---------------------------
                    # PRICE DETAILS
                    # ---------------------------

                    "price_details": {
                        "subtotal": float(order.subtotal),
                        "product_discount": float(order.discount_amount),
                        "coupon_discount": float(order.coupon_discount),
                        "shipping_charge": float(order.shipping_charge),
                        "tax_amount": float(order.tax_amount),
                        "total_amount": float(order.total_amount),
                        "total_you_saved": float(total_saved_amount)
                    },

                    # ---------------------------
                    # ORDERED PRODUCTS
                    # ---------------------------

                    "ordered_products": order_items_response,

                    # ---------------------------
                    # RAZORPAY DATA
                    # ---------------------------

                    "razorpay": razorpay_order_data
                }
            }

            return Response(
                response_data,
                status=status.HTTP_201_CREATED
            )

        except Exception as e:

            return Response(
                {
                    "status": "error",
                    "message": f"{INTERNAL_SERVER_ERROR} - Internal Server Error : {str(e)}"
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