from ...views import *



class ProductFilterAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try:
            category = request.GET.get("category")
            subcategory = request.GET.get("subcategory")
            size = request.GET.get("size")
            search = request.GET.get("search")

            products = Product.objects.filter(is_deleted=False,is_deactive=False)

            if search:
                products = products.filter(
                    Q(name__icontains=search) |
                    Q(description__icontains=search) |
                    Q(category__icontains=search) |
                    Q(subcategory__icontains=search)
                )

            if category:
                category_list = category.split(",")
                products = products.filter(category__in=category_list)


            if subcategory:
                subcategory_list = subcategory.split(",")
                products = products.filter(subcategory__in=subcategory_list)

            if size:
                size_list = size.split(",")

                query = Q()
                for s in size_list:
                    query |= Q(sizes__icontains=s)

                products = products.filter(query)

            min_price = request.GET.get("min_price")
            max_price = request.GET.get("max_price")

            if min_price:
                products = products.filter(price__gte=min_price)

            if max_price:
                products = products.filter(price__lte=max_price)

            bestseller = request.GET.get("bestseller")
            if bestseller == "true":
                products = products.filter(is_bestseller=True)

            latest = request.GET.get("latest")
            if latest == "true":
                products = products.filter(is_latest_arrival=True)

            in_stock = request.GET.get("in_stock")
            if in_stock == "true":
                products = products.filter(stock__gt=0)

            sort_by = request.GET.get("sort_by")
            if sort_by == "price_low_to_high":
                products = products.order_by("price")

            elif sort_by == "price_high_to_low":
                products = products.order_by("-price")

            elif sort_by == "latest":
                products = products.order_by("-created_at")

            elif sort_by == "oldest":
                products = products.order_by("created_at")

            elif sort_by == "discount":
                products = products.order_by("-discount_percentage")

            else:
                products = products.order_by("-created_at")

            serializer = ProductListSerializer(products,many=True,context={"request": request})

            categories = Product.objects.filter(is_deleted=False,is_deactive=False).values_list("category",flat=True).distinct()
            subcategories = Product.objects.filter(is_deleted=False,is_deactive=False).values_list("subcategory",flat=True).distinct()
            price_range = Product.objects.filter(is_deleted=False,is_deactive=False).aggregate(min_price=Min("price"),max_price=Max("price"))

            response_data = {
                "status": "success",
                "message": f"{SUCCESS} - Products Fetched Successfully",
                "total_products": products.count(),
                "filters": {
                    "categories": list(categories),
                    "subcategories": list(subcategories),
                    "price_range": price_range
                },
                "data": serializer.data
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"status": "error","message":f"{INTERNAL_SERVER_ERROR} - Internal server error: {str(e)} "}, 
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)