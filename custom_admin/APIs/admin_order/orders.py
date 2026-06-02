from ...views import *



class AdminOrderListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def get(self, request):
        try:
            
            orders = Order.objects.all().order_by('-order_date')

            status_filter = request.GET.get('status')
            if status_filter:
                orders = orders.filter(status=status_filter)

            serializer = OrderListSerializer(orders, many=True)

            response_data = {
                "status": "success",
                "message": f"{SUCCESS} - Orders fetched successfully",
                "data": {
                    "total_items": orders.count(),
                    "results": serializer.data
                }
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"status": "error","message": f"{INTERNAL_SERVER_ERROR} - Internal Server Error: {str(e)}"}, 
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)



class AdminOrderDetailAPIView(APIView):
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def get(self, request, order_id):
        try:
            order = Order.objects.filter(order_id=order_id).first()

            if not order:
                return Response({
                    'status': 'fail',
                    'message': f'{NOT_FOUND} - Order not found'
                }, status=status.HTTP_404_NOT_FOUND)

            serializer = OrderSerializer(order)

            return Response({
                'status': 'success',
                'message': f'{SUCCESS} - Order details fetched successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'{INTERNAL_SERVER_ERROR} - {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)