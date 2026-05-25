from ...views import *



class AdminReturnApproveAPIView(APIView):
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def put(self, request, order_id):
        try:
            action = request.data.get('action')
            admin_notes = request.data.get('admin_notes')

            required = ['action']
            missing = check_missing_fields(request.data, required)
            if missing:
                return missing

            if action not in ['approve', 'reject']:
                return Response({'status': 'fail','message': f'{BAD_REQUEST} - Action must be approve or reject'}, 
                                status=status.HTTP_400_BAD_REQUEST)

            with transaction.atomic():
                order = Order.objects.get(order_id=order_id)
                if action == 'approve':
                    order.admin_notes = admin_notes
                    order.save()
                    update_order_status(order, 'RETURN_APPROVED', description='Return approved by admin')
                    
                    if order.payment_method != 'COD' and order.payment_status == 'PAID':
                        order.payment_status = 'REFUNDED'
                        order.refunded_at = timezone.now()
                        order.save()
                else:  
                    update_order_status(order, 'DELIVERED', description='Return request rejected')
                    for item in order.items.all():
                        item.is_return_requested = False
                        item.return_reason = ''
                        item.save()

                return Response({'status': 'success','message': f'{SUCCESS} - Return {action}d successfully'}, 
                                status=status.HTTP_200_OK)

        except Order.DoesNotExist:
            return Response({'status': 'fail','message': f'{NOT_FOUND} - Order not found'}, 
                            status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({'status': 'error','message': f'{INTERNAL_SERVER_ERROR} - Internal Server Error : {str(e)}'}, 
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)