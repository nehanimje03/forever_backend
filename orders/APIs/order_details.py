from ..views import *


class OrderDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        try:
            order = Order.objects.filter(order_id=order_id,user=request.user).first()
            if not order:
                return Response({"status": "fail","message": f"{NOT_FOUND} - Order not found",},
                                status=status.HTTP_404_NOT_FOUND)

            serializer = OrderSerializer(order)

            response_data = {
                "status": "success",
                "message": f"{SUCCESS} - Order fetched successfully",
                "data": serializer.data
            },
            return Response(response_data,status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"status": "error","message": f"{INTERNAL_SERVER_ERROR} - Internal server error: {str(e)}",},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)