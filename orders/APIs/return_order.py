from ..views import *


class ReturnOrderAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):
        try:
            return_reason = request.data.get('return_reason', '')

            required = ['return_reason']
            missing = check_missing_fields(request.data, required)
            if missing:
                return missing
            
            order = Order.objects.get(order_id=order_id, user=request.user)
            if not order.can_return:
                return Response({'status': 'fail','message': f'{BAD_REQUEST} - Order cannot be returned. Return window is 7 days from delivery.'}, 
                                status=status.HTTP_400_BAD_REQUEST)


            with transaction.atomic():
                update_order_status(order, 'RETURN_REQUESTED', description=f'Return requested: {return_reason}')
                for item in order.items.all():
                    item.is_return_requested = True
                    item.return_reason = return_reason
                    item.return_requested_at = timezone.now()
                    item.save()

                return Response({'status': 'success','message': f'{SUCCESS} - Return request submitted successfully'}, 
                                status=status.HTTP_200_OK)

        except Order.DoesNotExist:
            return Response({'status': 'fail','message': f'{NOT_FOUND} - Order not found'}, 
                            status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({'status': 'error','message': f'{INTERNAL_SERVER_ERROR} - Internal Server Error : {str(e)}'}, 
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)