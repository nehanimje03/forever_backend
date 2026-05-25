from ...views import *


class AdminUpdateOrderStatusAPIView(APIView):
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def put(self, request, order_id):
        try:
            status_value = request.data.get("status")
            location = request.data.get("location")
            description = request.data.get("description")

            required = ['status']
            missing = check_missing_fields(request.data, required)
            if missing:
                return missing

            order = Order.objects.filter(order_id=order_id).first()
            if not order:
                return Response({'status': 'fail','message': f'{NOT_FOUND} - Order not found'}, 
                                status=status.HTTP_404_NOT_FOUND)

            if status_value not in dict(Order.ORDER_STATUS_CHOICES):
                return Response({'status': 'fail','message': f'{BAD_REQUEST} - Invalid status'}, 
                                status=status.HTTP_400_BAD_REQUEST)

            with transaction.atomic():
                update_order_status(order, status_value, location, description)

                if status_value == "DELIVERED":
                    order.delivered_at = timezone.now()
                    order.save()

            return Response({'status': 'success','message': f'{SUCCESS} - Order status updated to {status_value}'}, 
                            status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'status': 'error','message': f'{INTERNAL_SERVER_ERROR} - Internal Server Error : {str(e)}'}, 
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class AdminUpdatePaymentStatusAPIView(APIView):
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def put(self, request, order_id):
        try:
            payment_status = request.data.get("payment_status")
            payment_id = request.data.get("payment_id")

            required = ['payment_status']
            missing = check_missing_fields(request.data, required)
            if missing:
                return missing

            order = Order.objects.filter(order_id=order_id).first()
            if not order:
                return Response({'status': 'fail','message': f'{NOT_FOUND} - Order not found'}, 
                                status=status.HTTP_404_NOT_FOUND)


            if payment_status not in dict(Order.PAYMENT_STATUS_CHOICES):
                return Response({'status': 'fail','message': f'{BAD_REQUEST} - Invalid payment status'}, 
                                status=status.HTTP_400_BAD_REQUEST)

            order.payment_status = payment_status

            if payment_id:
                order.payment_id = payment_id

            order.save()

            response_data = {
                'status': 'success',
                'message': f'{SUCCESS} - Payment status updated successfully',
                'data': {
                    'order_id': order.order_id,
                    'payment_status': order.payment_status
                }
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'status': 'error','message': f'{INTERNAL_SERVER_ERROR} - Internal Server Error : {str(e)}'}, 
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)