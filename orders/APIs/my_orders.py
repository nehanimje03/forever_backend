from ..views import *


class MyOrdersAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            orders = (Order.objects.filter(user=request.user).prefetch_related('items').order_by('-id'))
            serializer = OrderListSerializer(orders, many=True)

            response_data = {
                "status": "success",
                "message": f"{SUCCESS} - My orders fetched successfully",
                "data": {
                    "total_orders": orders.count(),
                    "orders": serializer.data
                }
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"status": "error","message": f"{INTERNAL_SERVER_ERROR} - Internal Server Error : {str(e)}",}, 
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)