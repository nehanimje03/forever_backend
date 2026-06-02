from rest_framework import serializers
from .models import Order, OrderItem, OrderTracking, Coupon
from products.serializers import ProductListSerializer
from authentication.serializers import AddressSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    """Order Item Serializer"""
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    product_details = ProductListSerializer(source='product', read_only=True)
    
    class Meta:
        model = OrderItem
        fields = [
            'id', 'product', 'product_details', 'product_name', 'product_image',
            'product_price', 'original_price', 'discount_percentage',
            'quantity', 'size', 'color', 'subtotal',
            'is_return_requested', 'return_reason', 'return_status'
        ]


class OrderTrackingSerializer(serializers.ModelSerializer):
    """Order Tracking Serializer"""
    
    class Meta:
        model = OrderTracking
        fields = ['id', 'status', 'location', 'description', 'created_at']



class CreateOrderSerializer(serializers.Serializer):
    shipping_address_id = serializers.IntegerField()
    same_as_shipping = serializers.BooleanField(default=True)
    billing_address_id = serializers.IntegerField(required=False)
    payment_method = serializers.ChoiceField(choices=Order.PAYMENT_METHOD_CHOICES)
    coupon_code = serializers.CharField(max_length=50,required=False,allow_blank=True)
    order_note = serializers.CharField(required=False,allow_blank=True)




class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    tracking_history = OrderTrackingSerializer(many=True, read_only=True)

    total_items = serializers.IntegerField(read_only=True)
    order_status_display = serializers.CharField(read_only=True)
    can_cancel = serializers.BooleanField(read_only=True)
    can_return = serializers.BooleanField(read_only=True)

    customer = serializers.SerializerMethodField()
    shipping_address = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            # Basic Order Info
            'id',
            'order_id',
            'tracking_number',
            'order_date',
            'updated_at',

            # Customer
            'customer',

            # Order Summary
            'subtotal',
            'discount_amount',
            'coupon_code',
            'coupon_discount',
            'shipping_charge',
            'tax_amount',
            'total_amount',
            'total_items',

            # Shipping Address
            'shipping_address',

            # Raw Shipping Fields (optional)
            'shipping_name',
            'shipping_email',
            'shipping_phone',
            'shipping_alternate_phone',
            'shipping_address_line1',
            'shipping_address_line2',
            'shipping_landmark',
            'shipping_city',
            'shipping_state',
            'shipping_pincode',
            'shipping_country',

            # Billing
            'same_as_shipping',
            'billing_name',
            'billing_address',
            'billing_city',
            'billing_state',
            'billing_pincode',

            # Payment
            'payment_method',
            'payment_status',
            'payment_id',

            # Status
            'status',
            'order_status_display',
            'can_cancel',
            'can_return',
            'order_note',

            # Timestamps
            'confirmed_at',
            'processed_at',
            'packed_at',
            'shipped_at',
            'delivered_at',
            'cancelled_at',

            # Related Data
            'items',
            'tracking_history',
        ]

        read_only_fields = [
            'id',
            'order_id',
            'tracking_number',
            'order_date'
        ]

    def get_customer(self, obj):
        return {
            "id": obj.user.id if obj.user else None,
            "name": obj.shipping_name,
            "email": obj.shipping_email,
            "phone": obj.shipping_phone
        }

    def get_shipping_address(self, obj):
        return {
            "address": obj.shipping_address_line1,
            "address_line2": obj.shipping_address_line2,
            "landmark": obj.shipping_landmark,
            "city": obj.shipping_city,
            "state": obj.shipping_state,
            "pincode": obj.shipping_pincode,
            "country": obj.shipping_country
        }

class OrderListSerializer(serializers.ModelSerializer):
    """Minimal Order Serializer for List View"""
    total_items = serializers.IntegerField(read_only=True)
    order_status_display = serializers.CharField(read_only=True)
    
    class Meta:
        model = Order
        fields = [
            'id', 'order_id', 'order_date', 'total_amount',
            'total_items', 'status', 'order_status_display',
            'payment_status', 'payment_method'
        ]


class CouponSerializer(serializers.ModelSerializer):
    """Coupon Serializer"""
    is_valid = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Coupon
        fields = '__all__'
        read_only_fields = ['used_count', 'created_at']


class ValidateCouponSerializer(serializers.Serializer):
    """Validate Coupon Request Serializer"""
    coupon_code = serializers.CharField(max_length=50)
    subtotal = serializers.DecimalField(max_digits=10, decimal_places=2)