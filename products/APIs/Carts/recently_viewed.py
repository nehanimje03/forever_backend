from ...views import *

"""
API to track recent products when user views a product
Product ID will be sent in request body
"""
class TrackRecentProductAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            product_id = request.data.get('product_id')
            
            required_fields = ['product_id']
            missing = check_missing_fields(request.data, required_fields)
            if missing:
                return missing
            
            product = Product.objects.filter(id=product_id, is_deleted=False, is_deactive=False).first()
            if not product:
                return Response({'status': 'fail', 'message': f'{NOT_FOUND} - Product not found'}, 
                                status=status.HTTP_404_NOT_FOUND)
            
            recent, created = RecentProduct.objects.get_or_create(
                user=request.user,
                product=product,
                defaults={'viewed_at': timezone.now()}
            )
            
            if not created:
                recent.viewed_at = timezone.now()
                recent.save()
                        
            return Response({'status': 'success', 'message': f'{SUCCESS} - Product tracked successfully'}, 
                            status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({'status': 'error', 'message': f'{INTERNAL_SERVER_ERROR} - Internal server error - {str(e)}'}, 
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)



"""
API to get recent products for logged-in user
"""
class RecentProductsAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            limit = int(request.GET.get('limit', 10))
            
            recent_items = RecentProduct.objects.filter(
                user=request.user,
                product__is_deleted=False,
                product__is_deactive=False
            ).select_related('product')[:limit]
            
            products = [item.product for item in recent_items]
            serializer = ProductListSerializer(products, many=True,context={"request": request})
            
            return Response({'status': 'success','data': serializer.data}, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({'status': 'error', 'message': f'{INTERNAL_SERVER_ERROR} - Internal server error - {str(e)}'}, 
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)



"""
API to clear all recent products for logged-in user
"""
# class ClearRecentProductsAPIView(APIView):
#     permission_classes = [IsAuthenticated]
    
#     def delete(self, request):
#         try:
#             RecentProduct.objects.filter(user=request.user).delete()
                        
#             return Response({'status': 'success', 'message': f'{SUCCESS} - Recent products cleared successfully'}, 
#                             status=status.HTTP_200_OK)
        
#         except Exception as e:
#             return Response({'status': 'error', 'message': f'{INTERNAL_SERVER_ERROR} - Internal server error - {str(e)}'}, 
#                             status=status.HTTP_500_INTERNAL_SERVER_ERROR)