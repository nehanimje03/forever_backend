from ..views import *


class MyOrdersAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:

            orders = (
                Order.objects
                .filter(user=request.user)
                .prefetch_related(
                    Prefetch(
                        'items',
                        queryset=OrderItem.objects.select_related('product')
                    )
                )
                .order_by('-order_date')
            )

            orders_data = []

            for order in orders:
                items_data = []

                for item in order.items.all():
                    product = item.product
                    product_image = None

                    if item.product_image:
                        product_image = item.product_image

                    elif (product and hasattr(product, "image") and product.image):

                        product_image = request.build_absolute_uri(product.image.url)

                    items_data.append({
                        "order_item_id": item.id,
                        "product_id": product.id if product else None,
                        "product_name": item.product_name,
                        "product_image": product_image,
                        "price": str(item.product_price),
                        "quantity": item.quantity,
                        "size": item.size,
                        "color": item.color,
                        "item_total": str(item.subtotal),
                        "return_status": item.return_status,
                    })

                orders_data.append({
                    "order_id": order.order_id,
                    "order_status": order.status,
                    "order_status_display": (order.order_status_display),
                    "order_date": order.order_date,
                    "tracking_number": (order.tracking_number),
                    "payment": {
                        "method": order.payment_method,
                        "status": order.payment_status,
                    },
                    "price_summary": {
                        "subtotal": str(order.subtotal),
                        "discount": str(order.discount_amount),
                        "shipping_charge": str(order.shipping_charge),
                        "total_amount": str(order.total_amount),
                    },
                    "delivery_address": {
                        "name": order.shipping_name,
                        "phone": order.shipping_phone,
                        "city": order.shipping_city,
                        "state": order.shipping_state,
                        "pincode": order.shipping_pincode,
                    },
                    "can_cancel": (order.can_cancel),
                    "can_return": (order.can_return),
                    "total_items": (order.total_items),
                    "products": items_data,
                })

            response_data = {
                    "status": "success",
                    "message": (f"{SUCCESS} - ""My orders fetched successfully"),
                    "data": {
                        "total_orders": orders.count(),
                        "orders": orders_data
                    }
                }
            return Response(response_data ,status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"status": "error","message": (f"{INTERNAL_SERVER_ERROR}"f" - Internal Server Error : "f"{str(e)}")},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)