from ...views import *


class CartAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            if 'increase' in request.path or request.data.get('action') == 'increase':
                return self.increase_quantity(request)
            
            if 'decrease' in request.path or request.data.get('action') == 'decrease':
                return self.decrease_quantity(request)
            
            elif 'product_id' in request.data and 'quantity' in request.data:
                return self.add_to_cart(request)

            else:
                return Response({'status': 'fail', 'message': f'{BAD_REQUEST} - Invalid Request Parameters'},
                                status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'status': 'error', 'message': f'{INTERNAL_SERVER_ERROR} - {str(e)}'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def add_to_cart(self, request):
        try:
            product_id = int(request.data.get("product_id"))
            quantity = int(request.data.get("quantity"))

            required = ['product_id', 'quantity']
            missing = check_missing_fields(request.data, required)
            if missing:
                return missing

            if quantity <= 0:
                return Response({'status': 'fail','message': f'{BAD_REQUEST} - Quantity must be greater than 0'},
                                status=status.HTTP_400_BAD_REQUEST)

            size = request.data.get("size")
            color = request.data.get("color")

            product = Product.objects.filter(
                id=product_id,
                is_deleted=False,
                is_deactive=False
            ).first()

            if not product:
                return Response({'status': 'fail','message': f'{BAD_REQUEST} - Product not found'},
                                status=status.HTTP_400_BAD_REQUEST)

            if product.stock <= 0:
                return Response({'status': 'fail','message': f'{BAD_REQUEST} - Product is Out Of Stock'},
                                status=status.HTTP_400_BAD_REQUEST)

            quantity = min(quantity, product.stock)

            with transaction.atomic():
                cart, _ = Cart.objects.select_for_update().get_or_create(
                    user=request.user,
                    is_deleted=False,
                    defaults={'created_by': request.user}
                )

                cart_item = CartItem.objects.select_for_update().filter(
                    cart=cart,
                    product=product,
                    size=size,
                    color=color,
                    is_deleted=False
                ).first()

                if cart_item:
                    new_quantity = min(cart_item.quantity + quantity, product.stock)
                    cart_item.quantity = new_quantity
                    cart_item.updated_by = request.user
                    cart_item.save(update_fields=["quantity", "updated_by"])
                else:
                    cart_item = CartItem.objects.create(
                        cart=cart,
                        product=product,
                        size=size,
                        color=color,
                        quantity=quantity,
                        created_by=request.user
                    )

                cart.refresh_from_db()

            product_data = ProductListSerializer(product,context={"request": request}).data

            response_data = {
                "status": "success",
                "message": f"{SUCCESS} - Item added to cart",
                "data": {
                    "cart_id": cart.id,
                    "cart_item_id": cart_item.id,
                    "quantity": cart_item.quantity,
                    "cart_total_items": cart.total_items,
                    "cart_total_price": str(cart.total_price),
                    "product": product_data
                }
            }
            return Response(response_data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({'status': 'error', 'message': f'{INTERNAL_SERVER_ERROR} - Internal Server Error - {str(e)}'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def increase_quantity(self, request):
        try:
            cart_item_id = int(request.data.get("product_id"))

            required_fields = ['product_id']
            missing = check_missing_fields(request.data, required_fields)
            if missing:
                return missing

            with transaction.atomic():
                cart_item = (
                    CartItem.objects
                    .select_related("cart", "product")
                    .select_for_update()
                    .get(id=cart_item_id, is_deleted=False)
                )

                if cart_item.cart.user != request.user:
                    return Response({'status': 'fail', 'message': f'{UNAUTHORIZED} - Unauthorized access'},
                                    status=status.HTTP_403_FORBIDDEN)

                if cart_item.product.stock <= 0:
                    return Response({'status': 'fail','message': f'{BAD_REQUEST} - Product is Out Of Stock'},
                                    status=status.HTTP_400_BAD_REQUEST)

                if cart_item.quantity >= cart_item.product.stock:
                    return Response({'status': 'fail','message': f'{BAD_REQUEST} - Stock limit reached'},
                                    status=status.HTTP_400_BAD_REQUEST)

                cart_item.quantity += 1
                cart_item.save(update_fields=["quantity"])

                cart_item.cart.refresh_from_db()

            product_data = ProductListSerializer(cart_item.product,context={"request": request}).data

            response_data = {
                "status": "success",
                "message": f"{SUCCESS} - Quantity increased successfully",
                "data": {
                    "cart_item_id": cart_item.id,
                    "new_quantity": cart_item.quantity,
                    "item_subtotal": float(cart_item.product.price * cart_item.quantity),
                    "cart_total_items": cart_item.cart.total_items,
                    "cart_total_price": str(cart_item.cart.total_price),
                    "product": product_data
                }
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except CartItem.DoesNotExist:
            return Response({'status': 'fail', 'message': f'{NOT_FOUND} - Cart item not found.'},
                            status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({'status': 'error', 'message': f'{INTERNAL_SERVER_ERROR} - Internal Server Error - {str(e)}'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def decrease_quantity(self, request):
        try:
            required_fields = ['product_id']
            missing = check_missing_fields(request.data, required_fields)
            if missing:
                return missing

            cart_item_id = int(request.data.get("product_id"))

            with transaction.atomic():
                cart_item = (
                    CartItem.objects
                    .select_related("cart", "product")
                    .select_for_update()
                    .get(id=cart_item_id, is_deleted=False)
                )

                if cart_item.cart.user != request.user:
                    return Response({'status': 'fail','message': f'{UNAUTHORIZED} - Unauthorized access'},
                                    status=status.HTTP_403_FORBIDDEN)

                cart_item.quantity -= 1

                if cart_item.quantity <= 0:
                    cart_item.is_deleted = True
                    cart_item.save(update_fields=["is_deleted"])
                    item_removed = True
                    message = "Item removed from cart"
                else:
                    cart_item.save(update_fields=["quantity"])
                    item_removed = False
                    message = "Quantity decreased successfully"

                cart_item.cart.refresh_from_db()

            product_data = ProductListSerializer(cart_item.product,context={"request": request}).data

            response_data = {
                'status': 'success',
                'message': f'{SUCCESS} - {message}',
                'data': {
                    'cart_item_id': cart_item.id,
                    'item_removed': item_removed,
                    'cart_total_items': cart_item.cart.total_items,
                    'cart_total_price': str(cart_item.cart.total_price),
                    'product': product_data
                }
            }

            if not item_removed:
                response_data['data']['new_quantity'] = cart_item.quantity
                response_data['data']['item_subtotal'] = float(cart_item.product.price * cart_item.quantity)

            return Response(response_data, status=status.HTTP_200_OK)

        except CartItem.DoesNotExist:
            return Response({'status': 'fail','message': f'{NOT_FOUND} - Cart item not found.'},
                            status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({'status': 'error','message': f'{INTERNAL_SERVER_ERROR} - Internal Server Error - {str(e)}'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get(self, request):
        try:
            cart = Cart.objects.filter(user=request.user,is_deleted=False).first()

            if not cart:
                return Response({'status': 'fail','message': f'{NOT_FOUND} - Cart not found'},
                                status=status.HTTP_404_NOT_FOUND)

            queryset = (
                CartItem.objects
                .filter(cart=cart,is_deleted=False)
                .select_related('product')
                .order_by('-pk')
            )

            serializer = CartItemSerializer(queryset,many=True,context={'request':request})

            return Response({
                'status': 'success',
                'message': f'{SUCCESS} - Cart Data Fetched Successfully',
                'data': {
                    'cart_summary': {
                        'total_items': cart.total_items,
                        'total_price': str(cart.total_price)
                    },
                    'results': serializer.data
                }
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'status': 'error','message': f'{INTERNAL_SERVER_ERROR} - Internal Server Error - {str(e)}'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def put(self, request):
        try:
            required_fields = ['product_id', 'quantity']
            missing = check_missing_fields(request.data, required_fields)
            if missing:
                return missing

            cart_item_id = int(request.data.get("product_id"))
            quantity = int(request.data.get("quantity"))

            if quantity <= 0:
                return Response({"status": "fail","message": f"{BAD_REQUEST} - Quantity must be greater than 0"},
                                status=status.HTTP_400_BAD_REQUEST)

            with transaction.atomic():
                cart_item = (
                    CartItem.objects
                    .select_related("cart", "product")
                    .select_for_update()
                    .filter(id=cart_item_id, is_deleted=False)
                    .first()
                )

                if not cart_item:
                    return Response({'status': 'fail','message': f'{NOT_FOUND} - Cart item not found'},status=status.HTTP_404_NOT_FOUND)

                if cart_item.cart.user != request.user:
                    return Response({'status': 'fail','message': f'{UNAUTHORIZED} - Unauthorized access'},
                                    status=status.HTTP_403_FORBIDDEN)

                if cart_item.product.stock <= 0:
                    return Response({
                        'status': 'fail',
                        'message': f'{BAD_REQUEST} - Product is Out Of Stock'
                    }, status=status.HTTP_400_BAD_REQUEST)

                if quantity > cart_item.product.stock:
                    quantity = cart_item.product.stock

                cart_item.quantity = quantity
                cart_item.updated_by = request.user
                cart_item.save(update_fields=["quantity", "updated_by"])

                cart_item.cart.refresh_from_db()

            response_data = {
                "status": "success",
                "message": f"{SUCCESS} - Cart updated successfully",
                "data": {
                    "cart_item_id": cart_item_id,
                    "new_quantity": quantity,
                    "cart_total_items": cart_item.cart.total_items,
                    "cart_total_price": str(cart_item.cart.total_price),
                }
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'status': 'error','message': f'{INTERNAL_SERVER_ERROR} - Internal Server Error - {str(e)}'},status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def delete(self, request):
        try:
            cart_item_id = request.data.get("product_id")

            required_fields = ['product_id']
            missing = check_missing_fields(request.data, required_fields)
            if missing:
                return missing

            cart_item_id = int(cart_item_id)

            with transaction.atomic():
                cart_item = (
                    CartItem.objects
                    .select_related("cart")
                    .select_for_update()
                    .filter(id=cart_item_id,is_deleted=False)
                    .first()
                )

                if not cart_item:
                    return Response({'status': 'fail','message': f'{BAD_REQUEST} - Item already removed'},status=status.HTTP_400_BAD_REQUEST)

                if cart_item.cart.user != request.user:
                    return Response({'status': 'fail','message': f'{UNAUTHORIZED} - Unauthorized access'},
                                    status=status.HTTP_403_FORBIDDEN)

                cart_item.is_deleted = True
                cart_item.updated_by = request.user
                cart_item.save(update_fields=['is_deleted', 'updated_by'])
                cart_item.cart.refresh_from_db()

            response_data = {
                'status': 'success',
                'message': f'{SUCCESS} - Item removed from cart successfully',
                'data': {
                    'removed_cart_item_id': cart_item_id,
                    'cart_total_items': cart_item.cart.total_items,
                    'cart_total_price': str(cart_item.cart.total_price)
                }
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'status': 'error','message': f'{INTERNAL_SERVER_ERROR} - Internal Server Error - {str(e)}'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)