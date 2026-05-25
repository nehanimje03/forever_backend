from ...views import *


class PublicProductDetailAPIView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        try:
            product_id = request.GET.get('product_id')

            required_fields = ['product_id']
            missing = check_missing_fields(request.GET, required_fields)
            if missing:
                return missing
            
            int_error = integer_field_validator(request, ['product_id'])
            if int_error:
                return int_error

            product = Product.objects.get(id=product_id, is_deleted=False, is_deactive=False)
            serializer = ProductSerializer(product, context={"request": request})

            related = Product.objects.filter(
                category=product.category,
                is_deleted=False,
                is_deactive=False
            ).exclude(id=product.id).order_by('-is_bestseller', '-created_at')[:8]
            related_serializer = ProductListSerializer(related, many=True,context={"request": request})

            response_data = {
                'status': 'success',
                'data': {
                    'product': serializer.data,
                    'related_products': related_serializer.data,
                    'related_count': related.count()
                }
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Product.DoesNotExist:
            return Response({'status': 'fail', 'message': f'{NOT_FOUND} - Product not found'}, 
                            status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({'status': 'error', 'message': f'{INTERNAL_SERVER_ERROR} - Internal Server Error - {str(e)}'}, 
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)