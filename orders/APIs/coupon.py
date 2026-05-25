from ..views import *


class ValidateCouponAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            coupon_code = request.data.get("coupon_code")
            subtotal = request.data.get("subtotal")

            required = ["coupon_code", "subtotal"]
            missing = check_missing_fields(request.data, required)
            if missing:
                return missing

            subtotal = Decimal(str(subtotal))
            coupon = Coupon.objects.filter(code__iexact=coupon_code.strip(),is_deleted=False).first()

            if not coupon:
                return Response({"status": "fail","message": f"{NOT_FOUND} - Invalid coupon code",}, 
                                status=status.HTTP_404_NOT_FOUND)

            if not coupon.is_valid():
                return Response({"status": "fail","message": f"{BAD_REQUEST} - Coupon expired or inactive"}, 
                                status=status.HTTP_400_BAD_REQUEST)

            if subtotal < coupon.min_order_amount:
                return Response({"status": "fail","message": f"{BAD_REQUEST} - Minimum order amount not met"}, 
                                status=status.HTTP_400_BAD_REQUEST)

            discount = Decimal("0.00")
            if coupon.discount_type == "PERCENTAGE":
                discount = (subtotal *Decimal(coupon.discount_value)) / Decimal("100")

                if coupon.max_discount_amount:
                    discount = min(discount,Decimal(coupon.max_discount_amount))
            else:
                discount = Decimal(coupon.discount_value)

            discount = discount.quantize(Decimal("0.01"))
            final_total = (subtotal - discount).quantize(Decimal("0.01"))

            response_data = {
                "status": "success",
                "message": f"{SUCCESS} - Coupon applied successfully",
                "data": {
                    "coupon": {
                        "id": coupon.id,
                        "code": coupon.code,
                        "title": coupon.title,
                        "description": coupon.description,
                        "discount_type": coupon.discount_type,
                        "discount_value": str(coupon.discount_value),
                        "max_discount_amount": (
                            str(coupon.max_discount_amount)
                            if coupon.max_discount_amount
                            else None
                        ),
                        "min_order_amount": str(coupon.min_order_amount),
                        "is_stackable": coupon.is_stackable,
                        "valid_from": coupon.valid_from,
                        "valid_to": coupon.valid_to,
                    },
                    "calculation": {
                        "subtotal": str(subtotal),
                        "discount_applied": str(discount),
                        "final_total": str(final_total),
                        "currency": "INR"
                    },
                    "coupon_applied": True,
                    "is_valid": True
                }
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"status": "error","message": f"{INTERNAL_SERVER_ERROR} - Internal Server Error: {str(e)}",}, 
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)