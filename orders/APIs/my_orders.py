from ..views import *
from django.db.models import Prefetch


class MyOrdersAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            orders = (Order.objects.filter(user=request.user).prefetch_related(Prefetch('items',queryset=OrderItem.objects.select_related('product'))).order_by('-id'))
            
            order_data = []
            for order in orders:
                items_data = []
                for item in order.items.all():
                    product = item.product
                    product_image = None

                    if item.product_image:
                        product_image = item.product_image

                    elif product and hasattr(product, 'image') and product.image:
                        product_image = request.build_absolute_uri(product.image.url)

                    items_data.append({
                        "order_item_id": item.id,
                        "product_id": product.id if product else None,
                        "product_name": item.product_name,
                        "product_description": getattr(product, "description", ""),
                        "category": getattr(product, "category", ""),
                        "subcategory": getattr(product, "subcategory", ""),
                        "brand": getattr(product, "brand", ""),
                        "sku": getattr(product, "sku", ""),
                        "product_image": product_image,
                        "price": str(item.product_price),
                        "original_price": str(item.original_price),
                        "discount_percentage": item.discount_percentage,
                        "quantity": item.quantity,
                        "total_price": str(item.subtotal),
                        "size": item.size,
                        "color": item.color,
                        "stock": getattr(product, "stock", 0),
                        "is_available": getattr(product, "is_available", True),
                        "is_latest_arrival": getattr(product, "is_latest_arrival", False),
                        "is_featured": getattr(product, "is_featured", False),
                        "is_best_seller": getattr(product, "is_best_seller", False),
                        "is_return_requested": item.is_return_requested,
                        "return_reason": item.return_reason,
                        "return_status": item.return_status,
                        "return_requested_at": item.return_requested_at,
                        "added_at": item.created_at,
                    })

                order_data.append({
                    "order_id": order.id,
                    "order_number": getattr(order, "order_number", f"ORD-{order.id}"),
                    "order_status": getattr(order, "status", ""),
                    "payment_method": getattr(order, "payment_method", ""),
                    "payment_status": getattr(order, "payment_status", ""),
                    "transaction_id": getattr(order, "transaction_id", None),
                    "order_date": getattr(order, "created_at", None),
                    "updated_at": getattr(order, "updated_at", None),
                    "subtotal": str(getattr(order, "subtotal", 0)),
                    "shipping_charge": str(getattr(order, "shipping_charge", 0)),
                    "discount": str(getattr(order, "discount", 0)),
                    "tax": str(getattr(order, "tax", 0)),
                    "total_amount": str(getattr(order, "total_amount", 0)),
                    "customer_details": {
                        "user_id": request.user.id,
                        "name": (
                            request.user.get_full_name()
                            if request.user.get_full_name()
                            else request.user.username
                        ),
                        "email": request.user.email,
                        "mobile_number": getattr(request.user, "mobile_number", ""),
                    },
                    "delivery_address": {
                        "full_name": getattr(order, "full_name", ""),
                        "mobile_number": getattr(order, "mobile_number", ""),
                        "alternate_mobile_number": getattr(order, "alternate_mobile_number", ""),
                        "address_line_1": getattr(order, "address_line_1", ""),
                        "address_line_2": getattr(order, "address_line_2", ""),
                        "landmark": getattr(order, "landmark", ""),
                        "city": getattr(order, "city", ""),
                        "state": getattr(order, "state", ""),
                        "country": getattr(order, "country", ""),
                        "pincode": getattr(order, "pincode", ""),
                    },
                    "products": items_data,
                    "total_products": len(items_data),
                })

            response_data = {
                "status": "success",
                "message": f"{SUCCESS} - My orders fetched successfully",
                "data": {
                    "total_orders": orders.count(),
                    "orders": order_data
                }
            }
            return Response(response_data,status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"status": "error","message": f"{INTERNAL_SERVER_ERROR} - Internal Server Error : {str(e)}",},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)