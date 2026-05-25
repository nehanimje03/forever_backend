from django.utils import timezone
from orders.models import *

def add_tracking_entry(order, status, description, location=None):
    return OrderTracking.objects.create(
        order=order,
        status=status,
        location=location,
        description=description
    )


from decimal import Decimal
from orders.models import Coupon


def calculate_order_summary(
        cart_items,
        coupon_code=None,
        shipping_charge=Decimal("0.00"),
        tax_rate=Decimal("0.18")
):

    subtotal = Decimal("0.00")

    for item in cart_items:
        subtotal += item.product.price * item.quantity

    discount_amount = Decimal("0.00")
    coupon_discount = Decimal("0.00")
    coupon_details = None

    if coupon_code:
        try:
            coupon = Coupon.objects.get(
                code=coupon_code.upper(),
                is_active=True
            )

            if coupon.is_valid() and subtotal >= coupon.min_order_amount:

                if coupon.discount_type == 'PERCENTAGE':
                    coupon_discount = (
                        subtotal * coupon.discount_value
                    ) / Decimal("100")

                    if coupon.max_discount_amount:
                        coupon_discount = min(
                            coupon_discount,
                            coupon.max_discount_amount
                        )
                else:
                    coupon_discount = coupon.discount_value

                discount_amount = coupon_discount
                coupon_details = coupon

        except Coupon.DoesNotExist:
            pass

    taxable_amount = subtotal - discount_amount

    tax_amount = taxable_amount * tax_rate

    total_amount = (
        subtotal
        - discount_amount
        + shipping_charge
        + tax_amount
    )

    return {
        'subtotal': round(subtotal, 2),
        'discount_amount': round(discount_amount, 2),
        'coupon_code': coupon_code,
        'coupon_discount': round(coupon_discount, 2),
        'shipping_charge': round(shipping_charge, 2),
        'tax_amount': round(tax_amount, 2),
        'total_amount': round(total_amount, 2),
        'coupon_details': coupon_details,
    }

def update_order_status(order, new_status, location=None, description=None):
    """Update order status and add tracking entry"""
    from django.utils import timezone
    
    status_messages = {
        'CONFIRMED': 'Your order has been confirmed',
        'PROCESSING': 'Your order is being processed',
        'PACKED': 'Your order has been packed',
        'SHIPPED': 'Your order has been shipped',
        'OUT_FOR_DELIVERY': 'Your order is out for delivery',
        'DELIVERED': 'Your order has been delivered',
        'CANCELLED': 'Your order has been cancelled',
        'RETURN_REQUESTED': 'Return request submitted',
        'RETURN_APPROVED': 'Return has been approved',
        'RETURNED': 'Order has been returned',
        'REFUNDED': 'Refund has been processed',
    }
    
    # Update timestamp fields
    timestamp_fields = {
        'CONFIRMED': 'confirmed_at',
        'PROCESSING': 'processed_at',
        'PACKED': 'packed_at',
        'SHIPPED': 'shipped_at',
        'DELIVERED': 'delivered_at',
        'CANCELLED': 'cancelled_at',
        'RETURNED': 'returned_at',
        'REFUNDED': 'refunded_at',
    }
    
    order.status = new_status
    if new_status in timestamp_fields:
        setattr(order, timestamp_fields[new_status], timezone.now())
    order.save()
    
    # Add tracking entry
    desc = description or status_messages.get(new_status, f"Order status updated to {new_status}")
    add_tracking_entry(order, new_status, desc, location)