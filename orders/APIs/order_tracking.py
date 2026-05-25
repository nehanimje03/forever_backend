from ..views import *


class OrderTrackingAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        try:
            order = (Order.objects.prefetch_related('tracking_history').filter(order_id=order_id, user=request.user).first())
            if not order:
                return Response({"status": "fail","message": f"{NOT_FOUND} - Order not found"},
                                status=status.HTTP_404_NOT_FOUND)

            tracking_history = order.tracking_history.all().order_by('created_at')
            history = [
                {
                    "status": track.status,
                    "location": track.location,
                    "description": track.description,
                    "timestamp": track.created_at
                }
                for track in tracking_history
            ]

            response_data = {
                "status": "success",
                "message": f"{SUCCESS} - Tracking fetched successfully",
                "data": {
                    "order_id": order.order_id,
                    "current_status": order.status,
                    "tracking_number": order.tracking_number,
                    "history": history
                }
            }
            return Response(response_data,status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"status": "error","message": f"{INTERNAL_SERVER_ERROR} - Internal server error: {str(e)}",},
                                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)