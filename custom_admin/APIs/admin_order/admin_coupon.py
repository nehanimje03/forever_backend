from ...views import *


class AdminCouponListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def get(self, request):
        try:
            coupons = Coupon.objects.filter(is_deleted=False).order_by('-id')
            serializer = CouponSerializer(coupons, many=True)

            response_data = {
                "status": "success",
                "message": "Coupons fetched successfully",
                "data": {
                    "results": serializer.data
                }
            }
            return Response(response_data,status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({"status": "error","message": f"{INTERNAL_SERVER_ERROR} - Internal server error: {str(e)}",},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def post(self, request):
        try:
            code = request.data.get("code").upper().strip()
            title = request.data.get("title")
            description = request.data.get("description")
            discount_type = request.data.get("discount_type")
            discount_value = request.data.get("discount_value")
            min_order_amount = request.data.get("min_order_amount", 0)
            max_discount_amount = request.data.get("max_discount_amount")
            usage_limit = request.data.get("usage_limit", 1)
            per_user_limit = request.data.get("per_user_limit", 1)
            valid_from = request.data.get("valid_from")
            valid_to = request.data.get("valid_to")
            is_stackable = request.data.get("is_stackable", False)
            applicable_products = request.data.get("applicable_products", [])

            required = ["code","title","discount_type","discount_value","valid_from","valid_to"]
            missing = check_missing_fields(request.data, required)
            if missing:
                return missing

            try:
                discount_value = Decimal(str(discount_value))
                min_order_amount = Decimal(str(min_order_amount))

                if max_discount_amount:
                    max_discount_amount = Decimal(str(max_discount_amount))
            except:
                return Response({
                    "status": "fail",
                    "message": f"{BAD_REQUEST} - Invalid amount format"
                }, status=status.HTTP_400_BAD_REQUEST)

            if discount_type not in ["PERCENTAGE", "FIXED"]:
                return Response({"status": "fail","message": f"{BAD_REQUEST} - Invalid discount type"}, 
                                status=status.HTTP_400_BAD_REQUEST)

            if discount_value <= 0:
                return Response({"status": "fail","message": f"{BAD_REQUEST} - Discount must be greater than 0"}, 
                                status=status.HTTP_400_BAD_REQUEST)

            if discount_type == "PERCENTAGE" and discount_value > 100:
                return Response({"status": "fail","message": f"{BAD_REQUEST} - Percentage cannot exceed 100%"}, 
                                status=status.HTTP_400_BAD_REQUEST)

            try:
                valid_from = timezone.datetime.fromisoformat(valid_from)
                valid_to = timezone.datetime.fromisoformat(valid_to)
            except:
                return Response({
                    "status": "fail",
                    "message": f"{BAD_REQUEST} - Invalid datetime format"
                }, status=status.HTTP_400_BAD_REQUEST)

            if valid_from >= valid_to:
                return Response({"status": "fail","message": f"{BAD_REQUEST} - Invalid coupon validity period"}, 
                                status=status.HTTP_400_BAD_REQUEST)

            with transaction.atomic():
                if Coupon.objects.filter(code__iexact=code).exists():
                    return Response({"status": "fail","message": f"{BAD_REQUEST} - Coupon already exists"}, 
                                    status=status.HTTP_400_BAD_REQUEST)

                coupon = Coupon.objects.create(
                    code=code,
                    title=title,
                    description=description,
                    discount_type=discount_type,
                    discount_value=discount_value,
                    min_order_amount=min_order_amount,
                    max_discount_amount=max_discount_amount,
                    usage_limit=usage_limit,
                    per_user_limit=per_user_limit,
                    valid_from=valid_from,
                    valid_to=valid_to,
                    is_stackable=is_stackable,
                )

                if applicable_products:
                    products = Product.objects.filter(
                        id__in=applicable_products,
                        is_deleted=False
                    )
                    coupon.applicable_products.add(*products)

                coupon.refresh_from_db()

            response_data = {
                "status": "success",
                "message": f"{SUCCESS} - Coupon created successfully",
                "data": {

                    "coupon_id": coupon.id,
                    "coupon_code": coupon.code,
                    "title": coupon.title,
                    "description": coupon.description,

                    "discount": {
                        "type": coupon.discount_type,
                        "value": str(coupon.discount_value),
                        "max_discount_amount": str(coupon.max_discount_amount) if coupon.max_discount_amount else None,
                    },

                    "order_rules": {
                        "min_order_amount": str(coupon.min_order_amount),
                        "usage_limit": coupon.usage_limit,
                        "per_user_limit": coupon.per_user_limit,
                        "used_count": coupon.used_count,
                        "is_stackable": coupon.is_stackable,
                    },

                    "validity": {
                        "valid_from": coupon.valid_from,
                        "valid_to": coupon.valid_to,
                        "is_currently_valid": coupon.is_valid()
                    },

                    "applicable_products": list(
                        coupon.applicable_products.values(
                            "id", "name"
                        )
                    ),

                    "created_at": coupon.created_at
                }
            }

            return Response(response_data, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"status": "error","message": f"{INTERNAL_SERVER_ERROR} - Internal Server Error: {str(e)}"}, 
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        




class AdminCouponDetailAPIView(APIView):
    permission_classes = [IsAuthenticated, IsSuperAdmin]

    def get(self, request, coupon_id):
        try:
            if not coupon_id:
                return Response({"status": "fail","message": f"{BAD_REQUEST} - coupon_id is required"},
                                status=status.HTTP_400_BAD_REQUEST)

            if not str(coupon_id).strip().lstrip("-").isdigit():
                return Response({"status": "fail","message": f"{BAD_REQUEST} - coupon_id must be an integer"},
                                status=status.HTTP_400_BAD_REQUEST)

            coupon_id = int(coupon_id)
            if coupon_id <= 0:
                return Response({"status": "fail","message": f"{BAD_REQUEST} - coupon_id must be greater than 0"},
                                status=status.HTTP_400_BAD_REQUEST)

            coupon = Coupon.objects.filter(id=coupon_id,is_deleted=False).first()
            if not coupon:
                return Response({"status": "fail","message": f"{NOT_FOUND} - Coupon not found"},
                                status=status.HTTP_404_NOT_FOUND)

            serializer = CouponSerializer(coupon)
            return Response(
                {
                    "status": "success",
                    "message": f"{SUCCESS} - Coupon fetched successfully",
                    "data": serializer.data
                },
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response({"status": "error","message": f"{INTERNAL_SERVER_ERROR} - Internal Server Error : {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)



    def put(self, request, coupon_id):
        try:
            coupon = Coupon.objects.filter(id=coupon_id).first()
            if not coupon:
                return Response({'status': 'fail','message': f'{NOT_FOUND} - Coupon not found'}, 
                                status=status.HTTP_404_NOT_FOUND)

            serializer = CouponSerializer(coupon, data=request.data, partial=True)

            if not serializer.is_valid():
                return Response({
                    'status': 'fail',
                    'message': 'Validation Error',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()

            return Response({
                'status': 'success',
                'message': f'{SUCCESS} - Coupon updated successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'{INTERNAL_SERVER_ERROR} - {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def delete(self, request, coupon_id):
        try:
            coupon = Coupon.objects.filter(id=coupon_id).first()

            if not coupon:
                return Response({
                    'status': 'fail',
                    'message': f'{NOT_FOUND} - Coupon not found'
                }, status=status.HTTP_404_NOT_FOUND)

            coupon.delete()

            return Response({
                'status': 'success',
                'message': f'{SUCCESS} - Coupon deleted successfully'
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                'status': 'error',
                'message': f'{INTERNAL_SERVER_ERROR} - {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)