from ...views import *


class ProductApiView(APIView):
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def post(self, request): 
        try:
            if 'page_number' in request.data and 'page_size' in request.data:
                return self.get_product(request)

            elif 'name' in request.data and 'price' in request.data :
                return self.create_product(request)

            else:
                return Response({'status': 'fail', 'message': f'{BAD_REQUEST} - Invalid Request Parameters'}, 
                                status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'status': 'error', 'message': f'{INTERNAL_SERVER_ERROR} - Internal server error: {str(e)}'}, 
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def create_product(self, request):
        try:
            name = request.data.get("name")
            price = request.data.get("price")
            description = request.data.get("description", "")
            stock = request.data.get("stock", 0)
            is_bestseller = str(request.data.get("is_bestseller", False)).lower() == "true"
            is_latest_arrival = str(request.data.get("is_latest_arrival", False)).lower() == "true"
            product_images = request.FILES.getlist("product_image")
            category = request.data.get("category")
            subcategory = request.data.get("subcategory")
            sizes = request.data.get("sizes")
            discount_percentage = request.data.get("discount_percentage", 0)

            required = ['name', 'price']
            missing = check_missing_fields(request.data, required)
            if missing:
                return missing

            price = float(price)
            discount_percentage = float(discount_percentage)

            error = image_files_type_validator(request, ['product_image'])
            if error:
                return error

            with transaction.atomic():
                if Product.objects.filter(name=name, is_deleted=False).exists():
                    return Response({'status': 'fail','message': f'{BAD_REQUEST} - Product name already exists'},
                                    status=status.HTTP_400_BAD_REQUEST)

                if sizes:
                    try:
                        if isinstance(sizes, str):
                            sizes = json.loads(sizes)

                        if isinstance(sizes, list):
                            sizes = ",".join(
                                [str(size).strip() for size in sizes if str(size).strip()]
                            )

                    except Exception:
                        if isinstance(sizes, str):
                            sizes = sizes.strip()

                product = Product.objects.create(
                    name=name,
                    price=price,
                    description=description,
                    stock=stock,
                    is_bestseller=is_bestseller,
                    is_latest_arrival=is_latest_arrival,
                    created_by=request.user,
                    category=category,
                    subcategory=subcategory,
                    sizes=sizes,
                    discount_percentage=discount_percentage
                )

                image_urls = []

                for image in product_images:
                    img_obj = ProductImage.objects.create(product=product,image=image)
                    image_urls.append(request.build_absolute_uri(img_obj.image.url))

                response_data = {
                    'status': 'success',
                    'message': f'{SUCCESS} - Product Created Successfully',
                    'data': {
                        'product_id': product.id,
                        'name': product.name,
                        'price': int(product.price) if product.price.is_integer() else float(product.price),                        
                        'description': product.description,
                        'stock': product.stock,
                        'is_bestseller': product.is_bestseller,
                        'is_latest_arrival': product.is_latest_arrival,
                        'is_dea'
                        'category': product.category,
                        'subcategory': product.subcategory,
                        'sizes': [size.strip() for size in product.sizes.split(',')] if product.sizes else [],
                        'discount_percentage': f"{int(product.discount_percentage)}%",                        
                        'created_by': product.created_by.id if product.created_by else None,
                        'product_image': image_urls
                    }
                }
                return Response(response_data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'status': 'error','message': f'{INTERNAL_SERVER_ERROR} - Internal server error: {str(e)}'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)    
    

    def get_product(self, request):
        try:
            product_id = request.data.get('product_id')
            is_bestseller = request.data.get('is_bestseller')
            is_latest_arrival = request.data.get('is_latest_arrival')
            order_by = request.data.get('order_by', "desc")
            search_query = request.data.get('search')
            category = request.data.get('category')
            subcategory = request.data.get('subcategory')

            missing = check_missing_fields(request.data, ['page_number', 'page_size'])
            if missing:
                return missing

            pagination = validate_pagination_fields(request)
            if isinstance(pagination, Response):
                return pagination

            page_number, page_size = pagination

            queryset = Product.objects.filter(is_deleted=False)
            if product_id:
                queryset = queryset.filter(pk=product_id)

            if is_bestseller:
                is_bestseller = str(is_bestseller).lower() == "true"
                queryset = queryset.filter(is_bestseller=is_bestseller)

            if is_latest_arrival:
                is_latest_arrival = str(is_latest_arrival).lower() == "true"
                queryset = queryset.filter(is_latest_arrival=is_latest_arrival)

            if category:
                queryset = queryset.filter(category=category)

            if subcategory:
                queryset = queryset.filter(subcategory=subcategory)

            if search_query:
                queryset = queryset.filter(
                    Q(name__icontains=search_query) |
                    Q(description__icontains=search_query) |
                    Q(category__icontains=search_query) |
                    Q(subcategory__icontains=search_query)
                )

            if order_by == "asc":
                queryset = queryset.order_by('pk')
            else:
                queryset = queryset.order_by('-pk')

            pagination_qs = paginate_queryset(queryset, page_number, page_size)
            if isinstance(pagination_qs, Response):
                return pagination_qs

            page_obj, paginator = pagination_qs

            serializer = ProductListSerializer(page_obj.object_list,many=True,context={"request": request})
            response_data = {
                'status': 'success',
                'message': f'{SUCCESS} - Product Data Fetched Successfully',
                'data': {
                    'total_pages': paginator.num_pages,
                    'current_page': page_obj.number,
                    'total_items': paginator.count,
                    'results': serializer.data
                }
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'status': 'error','message': f'{INTERNAL_SERVER_ERROR} - Internal server error: {str(e)}'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def put(self, request):
        try:
            product_id = request.query_params.get('product_id')
            name = request.data.get("name")
            price = request.data.get("price")
            description = request.data.get("description")
            stock = request.data.get("stock")
            is_bestseller = request.data.get("is_bestseller")
            is_latest_arrival = request.data.get("is_latest_arrival")
            product_image = request.FILES.getlist("product_image")
            category = request.data.get("category")
            subcategory = request.data.get("subcategory")
            sizes = request.data.get("sizes")
            discount_percentage = request.data.get("discount_percentage")

            missing = check_missing_fields(request.query_params, ['product_id'])
            if missing:
                return missing

            int_error = integer_field_validator(request, ['product_id'], source="params")
            if int_error:
                return int_error

            product = Product.objects.get(id=product_id, is_deleted=False)

            with transaction.atomic():
                if name and name.strip() != product.name:
                    duplicate_qs = Product.objects.filter(name=name.strip(),is_deleted=False).exclude(id=product_id)

                    if duplicate_qs.exists():
                        return Response({"status": "fail","message": f"{BAD_REQUEST} - Product name already exists."},
                                        status=status.HTTP_400_BAD_REQUEST)

                error = image_files_type_validator(request, ['product_image'])
                if error:
                    return error
                
                if product_image:
                    old_images = ProductImage.objects.filter(product=product)

                    for old in old_images:
                        if old.image:
                            old.image.delete(save=False)
                        old.delete()

                    for image in product_image:
                        ProductImage.objects.create(product=product, image=image)

                if sizes:
                    try:
                        if isinstance(sizes, str):
                            sizes = json.loads(sizes)

                        if isinstance(sizes, list):
                            sizes = ",".join(
                                [str(size).strip() for size in sizes if str(size).strip()]
                            )

                    except Exception:
                        if isinstance(sizes, str):
                            sizes = sizes.strip()

                if name:
                    product.name = name.strip()

                if price:
                    product.price = float(price)

                if description:
                    product.description = description

                if stock:
                    product.stock = int(stock)

                if is_bestseller:
                    product.is_bestseller = str(is_bestseller).lower() == "true"

                if is_latest_arrival:
                    product.is_latest_arrival = str(is_latest_arrival).lower() == "true"

                if category:
                    product.category = category

                if subcategory:
                    product.subcategory = subcategory

                if sizes:
                    product.sizes = sizes

                if discount_percentage:
                    discount_percentage = str(discount_percentage).replace('%', '')
                    product.discount_percentage = float(discount_percentage)

                product.updated_at = timezone.now()
                product.updated_by = request.user
                product.save()

            image_urls = [request.build_absolute_uri(img.image.url) for img in ProductImage.objects.filter(product=product)]
            actual_price = int(product.price) if product.price % 1 == 0 else float(product.price)

            response_data = {
                "status": "success",
                "message": f"{SUCCESS} - Product updated successfully",
                "data": {
                    "product_id": product.id,
                    "name": product.name,
                    "actual_price": actual_price,
                    "description": product.description,
                    "stock": product.stock,
                    "is_bestseller": product.is_bestseller,
                    "is_latest_arrival": product.is_latest_arrival,
                    "category": product.category,
                    "subcategory": product.subcategory,
                    "sizes": [size.strip() for size in product.sizes.split(",")] if product.sizes else [],                    
                    "discount_percentage": f"{int(product.discount_percentage)}%",
                    "product_images": image_urls
                }
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except Product.DoesNotExist:
            return Response({"status": "fail","message": f"{NOT_FOUND} - Product entry not found."},
                            status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"status": "error","message": f"{INTERNAL_SERVER_ERROR} - Internal server error: {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

    def delete(self, request):
        try:
            product_id = request.query_params.get('product_id')

            missing = check_missing_fields(request,['product_id'],source="params")
            if missing:
                return missing

            int_error = integer_field_validator(request,['product_id'],source="params")
            if int_error:
                return int_error

            product = Product.objects.filter(id=product_id,is_deleted=False).first()

            if not product:
                return Response({'status': 'fail','message': f'{NOT_FOUND} - Product not found.'},status=status.HTTP_404_NOT_FOUND)

            with transaction.atomic():
                product.is_deleted = True
                product.updated_at = timezone.now()
                product.updated_by = request.user
                product.save()

                response_data =  {'status': 'success','message': f'{SUCCESS} - Product Deleted Successfully'}
                return Response(response_data,status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'status': 'error','message': f'{INTERNAL_SERVER_ERROR} - Internal server error: {str(e)}'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)