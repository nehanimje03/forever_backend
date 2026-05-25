from ...views import *

class PublicProductsAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            product_type = request.GET.get('type', 'latest')
    
            if product_type == 'latest':
                products = Product.objects.filter(is_deleted=False,is_deactive=False,is_latest_arrival=True).order_by('-created_at')[:20]
                serializer = ProductListSerializer(products,many=True,context={"request": request})

                response_data = {
                    'status': 'success',
                    'message': f'{SUCCESS} - Latest Arrivals Fetched Successfully.',
                    'type': 'latest_arrivals',
                    'count': len(serializer.data),
                    'data': serializer.data
                }
                return Response(response_data, status=status.HTTP_200_OK)

            elif product_type == 'bestseller':
                products = Product.objects.filter(is_deleted=False,is_deactive=False,is_bestseller=True).order_by('-created_at')[:20]
                serializer = ProductListSerializer(products,many=True,context={"request": request})

                response_data = {
                    'status': 'success',
                    'message': f'{SUCCESS} - Best Sellers Fetched Successfully',
                    'type': 'bestsellers',
                    'count': len(serializer.data),
                    'data': serializer.data
                }
                return Response(response_data, status=status.HTTP_200_OK)

            elif product_type == 'all':
                page_number = int(request.GET.get('page_number', 1))
                page_size = int(request.GET.get('page_size', 12))
                search_query = request.GET.get('search')
                category = request.GET.get('category')
                min_price = request.GET.get('min_price')
                max_price = request.GET.get('max_price')
                sort_by = request.GET.get('sort_by', '-created_at')

                products = Product.objects.filter(is_deleted=False,is_deactive=False)
                if search_query:
                    products = products.filter(
                        Q(name__icontains=search_query) |
                        Q(description__icontains=search_query) |
                        Q(category__icontains=search_query) |
                        Q(subcategory__icontains=search_query)
                    )

                if category:
                    products = products.filter(category__iexact=category)
                    
                if min_price:
                    products = products.filter(price__gte=min_price)

                if max_price:
                    products = products.filter(price__lte=max_price)

                allowed_sort = ['price', '-price','name', '-name','created_at', '-created_at']
                if sort_by in allowed_sort:
                    products = products.order_by(sort_by)
                else:
                    products = products.order_by('-created_at')

                total_count = products.count()
                total_pages = (total_count + page_size - 1) // page_size

                start = (page_number - 1) * page_size
                end = start + page_size

                paginated_products = products[start:end]
                serializer = ProductListSerializer(paginated_products,many=True,context={'request': request})

                response_data = {
                    'status': 'success',
                    'message': f'{SUCCESS} - All Products Fetched Successfully',
                    'type': 'all_products',
                    'data': {
                        'products': serializer.data,
                        'pagination': {
                            'current_page': page_number,
                            'page_size': page_size,
                            'total_items': total_count,
                            'total_pages': total_pages,
                            'has_next': page_number < total_pages,
                            'has_previous': page_number > 1
                        }
                    }
                }
                return Response(response_data, status=status.HTTP_200_OK)

            else:
                return Response({'status': 'fail','message': f'{BAD_REQUEST} - Invalid type. Use latest, bestseller, all'}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'status': 'error','message': f'{INTERNAL_SERVER_ERROR} - Internal Server Error - {str(e)}'}, 
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)