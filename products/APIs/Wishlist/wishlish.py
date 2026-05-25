from ...views import *


class WishlistApiView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            product_id = request.data.get("product_id")

            required = ['product_id']
            missing = check_missing_fields(request.data, required)
            if missing:
                return missing

            int_error = integer_field_validator(request, ['product_id'])
            if int_error:
                return int_error

            product = Product.objects.filter(id=product_id,is_deleted=False,is_deactive=False).first()
            if not product:
                return Response({'status': 'fail','message': f'{BAD_REQUEST} - Product not found'}, 
                                status=status.HTTP_400_BAD_REQUEST)

            with transaction.atomic():
                wishlist, created = Wishlist.objects.get_or_create(
                    user=request.user,
                    defaults={'created_by': request.user}
                )
                existing_item = WishlistItem.objects.filter(wishlist=wishlist,product=product,is_deleted=False).exists()

                if existing_item:
                    return Response({'status': 'fail','message': f'{BAD_REQUEST} - Product already in wishlist'}, 
                                    status=status.HTTP_400_BAD_REQUEST)

                WishlistItem.objects.create(wishlist=wishlist,product=product,created_by=request.user)

                product_data = ProductListSerializer(product,context={"request": request}).data
                response_data = {
                    'status': 'success',
                    'message': f'{SUCCESS} - Product added to wishlist',
                    'data': {
                        'wishlist_id': wishlist.id,
                        'wishlist_total_items': wishlist.total_items,
                        'product': product_data
                    }
                }
                return Response(response_data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'status': 'error','message': f'{INTERNAL_SERVER_ERROR} - Internal server error: {str(e)}'}, 
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def get(self, request):
        try:
            wishlist = Wishlist.objects.filter(user=request.user,is_deleted=False).first()
            if not wishlist:
                return Response({'status': 'fail','message': f'{BAD_REQUEST} - Item Not Found In Wishlist.'},
                                status=status.HTTP_400_BAD_REQUEST)

            queryset = WishlistItem.objects.filter(wishlist=wishlist,is_deleted=False).select_related('product').order_by('-pk')
            serializer = WishlistItemSerializer(queryset, many=True, context={'request':request})
            
            response_data = {
                'status': 'success',
                'message': f'{SUCCESS} - Wishlist Data Fetched Successfully',
                'data': {
                    'wishlist_summary': {
                        'wishlist_id': wishlist.id,
                        'total_items': wishlist.total_items
                    },
                    'results': serializer.data
                }
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'status': 'error','message': f'{INTERNAL_SERVER_ERROR} - Internal server error: {str(e)}'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def delete(self, request):
        try:
            product_id = request.data.get("product_id")

            required = ['product_id']
            missing = check_missing_fields(request.data, required)
            if missing:
                return missing

            int_error = integer_field_validator(request, ['product_id'])
            if int_error:
                return int_error

            wishlist = Wishlist.objects.filter(user=request.user,is_deleted=False).first()
            if not wishlist:
                return Response({'status': 'fail', 'message': f'{NOT_FOUND} - Wishlist not found'},
                                status=status.HTTP_404_NOT_FOUND)

            wishlist_item = WishlistItem.objects.filter(wishlist=wishlist,product_id=product_id,is_deleted=False).first()
            if not wishlist_item:
                return Response({'status': 'fail', 'message': f'{NOT_FOUND} - Wishlist item not found.'},
                                status=status.HTTP_404_NOT_FOUND)

            with transaction.atomic():
                wishlist_item.is_deleted = True
                wishlist_item.updated_by = request.user
                wishlist_item.save(update_fields=['is_deleted', 'updated_by'])

            response_data = {
                'status': 'success',
                'message': f'{SUCCESS} - Item removed from wishlist successfully',
                'data': {
                    'removed_product_id': product_id,
                    'wishlist_id': wishlist.id,
                    'wishlist_total_items': wishlist.total_items
                }
            }
            return Response(response_data,status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'status': 'error','message': f'{INTERNAL_SERVER_ERROR} - Internal server error: {str(e)}'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)