# from ...views import *


# """
# This APIView is Used to clear Entire Cart
# """
# class CartClearAPIView(APIView):
#     permission_classes = [IsAuthenticated]

#     def delete(self, request):
#         try:
#             with transaction.atomic():
#                 cart = Cart.objects.filter(user=request.user, is_deleted=False).first()
                
#                 if cart:
#                     CartItem.objects.filter(cart=cart, is_deleted=False).update(is_deleted=True)
                    
#                 return Response({'status': 'success', 'message': f'{SUCCESS} - Cart cleared successfully'}, 
#                                 status=status.HTTP_200_OK)
                
#         except Exception as e:
#             return Response({'status': 'error', 'message': f'{INTERNAL_SERVER_ERROR} - {str(e)}'}, 
#                             status=status.HTTP_500_INTERNAL_SERVER_ERROR)