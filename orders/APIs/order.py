from ..views import *


class CreateOrderAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            shipping_address_id = request.data.get("shipping_address_id")
            payment_method = request.data.get("payment_method")
            coupon_code = request.data.get("coupon_code")
            products = request.data.get("products", [])

            required_fields = ["shipping_address_id","payment_method","products"]
            missing = check_missing_fields(request.data,required_fields)
            if missing:
                return missing

            if not isinstance(products, list) or len(products) == 0:
                return Response({"status": "fail","message": f"{BAD_REQUEST} - Products are required"},
                                status=status.HTTP_400_BAD_REQUEST)

            VALID_PAYMENT_METHODS = ["COD","CARD","UPI","NETBANKING","WALLET","EMI"]
            if payment_method not in VALID_PAYMENT_METHODS:
                return Response({"status": "fail","message": f"{BAD_REQUEST} - Invalid payment method"},
                                status=status.HTTP_400_BAD_REQUEST)
            user = request.user
            shipping_address = (Address.objects.filter(id=shipping_address_id,user=user,is_deleted=False).first())
            if not shipping_address:
                return Response({"status": "fail","message": f"{NOT_FOUND} - Shipping address not found"},
                                status=status.HTTP_404_NOT_FOUND)
            
            cart = (Cart.objects.select_for_update().filter(user=user,is_deleted=False).first())
            if not cart:
                return Response({"status": "fail","message": f"{NOT_FOUND} - Cart not found"},
                                status=status.HTTP_404_NOT_FOUND)

            cart_items = (CartItem.objects.select_related("product").select_for_update().filter(cart=cart,is_deleted=False))
            if not cart_items.exists():
                return Response({"status": "fail","message": f"{BAD_REQUEST} - Cart is empty"},
                                status=status.HTTP_400_BAD_REQUEST)

            request_product_ids = sorted([item.get("product_id") for item in products])
            cart_product_ids = sorted(
                list(cart_items.values_list("product_id",flat=True)))

            if request_product_ids != cart_product_ids:
                return Response({"status": "fail","message": f"{BAD_REQUEST} - Cart products mismatch"},
                                status=status.HTTP_400_BAD_REQUEST)

            subtotal = Decimal("0.00")
            total_discount = Decimal("0.00")
            total_saved_amount = Decimal("0.00")

            order_items_response = []
            razorpay_data = None

            with transaction.atomic():
                for item in cart_items:
                    product = (Product.objects.select_for_update().get(id=item.product.id))
                    if product.is_deleted or product.is_deactive:
                        return Response({"status": "fail","message": f"{BAD_REQUEST} - {product.name} unavailable"},
                                        status=status.HTTP_400_BAD_REQUEST)

                    if product.stock < item.quantity:
                        return Response({"status": "fail","message": (f"{BAD_REQUEST} - "f"Only {product.stock} stock left "f"for {product.name}")},
                                        status=status.HTTP_400_BAD_REQUEST)

                    mrp = Decimal(str(product.price))
                    discount_percentage = Decimal(str(product.discount_percentage or 0))
                    discount_amount = (mrp * discount_percentage) / Decimal("100")
                    selling_price = (mrp - discount_amount)
                    item_total = (selling_price * item.quantity)
                    saved_amount = (discount_amount * item.quantity)
                    subtotal += item_total
                    total_discount += saved_amount
                    total_saved_amount += saved_amount

                shipping_charge = (Decimal("0.00")if subtotal >= Decimal("500")else Decimal("100.00"))
                tax_amount = (subtotal * Decimal("0.18")) / Decimal("100")

                coupon_discount = Decimal("0.00")
                if coupon_code:
                    coupon = (Coupon.objects.filter(code=coupon_code,is_deleted=False,is_active=True).first())
                    if coupon:
                        coupon_discount = Decimal(str(coupon.discount_amount))

                total_amount = (subtotal + shipping_charge + tax_amount - coupon_discount)
                order = Order.objects.create(
                    user=user,
                    shipping_name=shipping_address.contact_name,
                    shipping_email=user.email,
                    shipping_phone=shipping_address.contact_no,
                    shipping_address_line1=(f"{shipping_address.house_no}, "f"{shipping_address.area_street}"),
                    shipping_address_line2=shipping_address.locality,
                    shipping_city=shipping_address.city,
                    shipping_state=shipping_address.state,
                    shipping_pincode=shipping_address.pincode,
                    shipping_country=shipping_address.country,
                    subtotal=subtotal,
                    discount_amount=total_discount,
                    coupon_code=coupon_code,
                    coupon_discount=coupon_discount,
                    shipping_charge=shipping_charge,
                    tax_amount=tax_amount,
                    total_amount=total_amount,
                    payment_method=payment_method,
                    payment_status=("COD"if payment_method == "COD"else "PENDING"),
                    status="PENDING",
                    created_by=user
                )
                for item in cart_items:
                    product = (Product.objects.select_for_update().get(id=item.product.id))
                    mrp = Decimal(str(product.price))
                    discount_percentage = Decimal(str(product.discount_percentage or 0))
                    discount_amount = (mrp * discount_percentage) / Decimal("100")
                    selling_price = (mrp - discount_amount)
                    item_total = (selling_price * item.quantity)

                    image = product.product_image.first()
                    image_url = (request.build_absolute_uri(image.image.url)if image else None)

                    order_item = OrderItem.objects.create(
                        order=order,
                        product=product,
                        product_name=product.name,
                        product_image=image_url,
                        product_price=selling_price,
                        original_price=mrp,
                        discount_percentage=int(discount_percentage),
                        quantity=item.quantity,
                        size=getattr(item, "size", None),
                        color=getattr(item, "color", None)
                    )

                    product.stock = (F("stock") - item.quantity)
                    product.save(update_fields=["stock"])

                    order_items_response.append({
                            "order_item_id": order_item.id,
                            "product_id": product.id,
                            "product_name": product.name,
                            "product_image": image_url,
                            "quantity": item.quantity,
                            "size": getattr(item,"size",None),
                            "color": getattr(item,"color",None),
                            "price_details": {
                                "mrp": float(mrp),
                                "selling_price": float(selling_price),
                                "discount_percentage": float(discount_percentage),
                                "saved_amount": float(discount_amount * item.quantity)
                            },
                            "total_amount": float(item_total)
                        }
                    )
                cart_items.update(is_deleted=True)
                add_tracking_entry(order,"PENDING","Order placed successfully")

                if payment_method != "COD":
                    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID,settings.RAZORPAY_KEY_SECRET))
                    razorpay_order = client.order.create({
                            "amount": int(total_amount * 100),
                            "currency": "INR",
                            "receipt": str(order.order_id),
                            "payment_capture": 1
                        }
                    )
                    order.payment_id = (razorpay_order["id"])
                    order.payment_response = (razorpay_order)
                    order.save(update_fields=["payment_id","payment_response"])
                    razorpay_data = {
                        "razorpay_order_id": (razorpay_order["id"]),
                        "razorpay_key": (settings.RAZORPAY_KEY_ID),
                        "amount": (razorpay_order["amount"]),
                        "currency": (razorpay_order["currency"])
                    }

                whatsapp_message = f"""
                    Your order has been placed successfully.
                    Order ID : {order.order_id}
                    Total Amount : ₹{order.total_amount}
                    Products :
                    """
                
                for item in order_items_response:
                    whatsapp_message += f"""
                        Product : {item['product_name']}
                        Quantity : {item['quantity']}
                        Price : ₹{item['total_amount']}
                        """

                whatsapp_message += """Thank you for shopping with us."""
                send_whatsapp_message(mobile=shipping_address.contact_no,message=whatsapp_message)

                Notify_Admin.objects.create(
                    title="New Order Received",
                    message=f"New order received - {order.order_id}",
                    order=order
                )

            response_data = {
                "status": "success",
                "message": "Order placed successfully",
                "data": {
                    "user_details": {
                        "user_id": user.id,
                        "full_name": (f"{user.first_name} "f"{user.last_name}").strip(),
                        "email": user.email,
                        "mobile_number": (shipping_address.contact_no)
                    },
                    "shipping_address": {
                        "name": (shipping_address.contact_name),
                        "mobile_number": (shipping_address.contact_no),
                        "full_address": (
                            f"{shipping_address.house_no}, "
                            f"{shipping_address.area_street}, "
                            f"{shipping_address.locality}, "
                            f"{shipping_address.city}, "
                            f"{shipping_address.state} - "
                            f"{shipping_address.pincode}"
                        ),
                        "city": (shipping_address.city),
                        "state": (shipping_address.state),
                        "country": (shipping_address.country),
                        "pincode": (shipping_address.pincode)
                    },

                    "order_details": {
                        "order_id": order.order_id,
                        "order_db_id": order.id,
                        "order_status": order.status,
                        "payment_method": (order.payment_method),
                        "payment_status": (order.payment_status),
                        "expected_delivery_date": (timezone.now() +timedelta(days=5)).date()
                    },

                    "price_details": {
                        "subtotal": float(order.subtotal),
                        "product_discount": float(order.discount_amount),
                        "coupon_discount": float(order.coupon_discount),
                        "shipping_charge": float(order.shipping_charge),
                        "tax_amount": float(order.tax_amount),
                        "total_amount": float(order.total_amount),
                        "total_saved_amount": float(total_saved_amount)
                    },
                    "ordered_products": (order_items_response),
                    "payment_gateway": (razorpay_data)
                }
            }
            return Response(response_data,status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"status": "error","message": (f"{INTERNAL_SERVER_ERROR} - Internal server error: {str(e)}")},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)            




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