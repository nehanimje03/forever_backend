from django.db import models
from django.contrib.auth import get_user_model
from products.models import Product
import uuid

User = get_user_model()

# class Order(models.Model):
#     """Main Order Model - Professional E-commerce Standard"""
    
#     # Order Status Choices
#     ORDER_STATUS_CHOICES = [
#         ('PENDING', 'Pending'),           # Order placed but not confirmed
#         ('CONFIRMED', 'Confirmed'),       # Order confirmed by admin
#         ('PROCESSING', 'Processing'),     # Order is being processed
#         ('PACKED', 'Packed'),             # Order is packed
#         ('SHIPPED', 'Shipped'),           # Order is shipped
#         ('OUT_FOR_DELIVERY', 'Out for Delivery'),  # Out for delivery
#         ('DELIVERED', 'Delivered'),       # Order delivered
#         ('CANCELLED', 'Cancelled'),       # Order cancelled
#         ('RETURN_REQUESTED', 'Return Requested'),  # Return requested
#         ('RETURN_APPROVED', 'Return Approved'),    # Return approved
#         ('RETURNED', 'Returned'),         # Returned
#         ('REFUNDED', 'Refunded'),         # Refunded
#     ]
    
#     # Payment Status Choices
#     PAYMENT_STATUS_CHOICES = [
#         ('PENDING', 'Pending'),           # Payment pending
#         ('PAID', 'Paid'),                 # Payment successful
#         ('FAILED', 'Failed'),             # Payment failed
#         ('REFUNDED', 'Refunded'),         # Refunded
#         ('COD', 'Cash on Delivery'),      # COD orders
#     ]
    
#     # Payment Method Choices
#     PAYMENT_METHOD_CHOICES = [
#         ('COD', 'Cash on Delivery'),
#         ('CARD', 'Credit/Debit Card'),
#         ('UPI', 'UPI'),
#         ('NETBANKING', 'Net Banking'),
#         ('WALLET', 'Wallet'),
#         ('EMI', 'EMI'),
#     ]
    
#     # ========== Order Identification ==========
#     order_id = models.CharField(max_length=20, unique=True, editable=False)
#     tracking_number = models.CharField(max_length=50, blank=True, null=True)
    
#     # ========== User Details ==========
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    
#     # ========== Shipping Address ==========
#     shipping_name = models.CharField(max_length=255)
#     shipping_email = models.EmailField()
#     shipping_phone = models.CharField(max_length=15)
#     shipping_alternate_phone = models.CharField(max_length=15, blank=True, null=True)
#     shipping_address_line1 = models.TextField()
#     shipping_address_line2 = models.TextField(blank=True, null=True)
#     shipping_landmark = models.CharField(max_length=255, blank=True, null=True)
#     shipping_city = models.CharField(max_length=100)
#     shipping_state = models.CharField(max_length=100)
#     shipping_pincode = models.CharField(max_length=10)
#     shipping_country = models.CharField(max_length=100, default='India')
    
#     # ========== Billing Address (same or different) ==========
#     same_as_shipping = models.BooleanField(default=True)
#     billing_name = models.CharField(max_length=255, blank=True, null=True)
#     billing_address = models.TextField(blank=True, null=True)
#     billing_city = models.CharField(max_length=100, blank=True, null=True)
#     billing_state = models.CharField(max_length=100, blank=True, null=True)
#     billing_pincode = models.CharField(max_length=10, blank=True, null=True)
    
#     # ========== Order Summary ==========
#     subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
#     discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
#     coupon_code = models.CharField(max_length=50, blank=True, null=True)
#     coupon_discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
#     shipping_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
#     tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
#     total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
#     # ========== Payment Details ==========
#     payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
#     payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='PENDING')
#     payment_id = models.CharField(max_length=255, blank=True, null=True)
#     payment_response = models.JSONField(blank=True, null=True)  # Store full payment response
    
#     # ========== Order Status ==========
#     status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='PENDING')
#     order_note = models.TextField(blank=True, null=True)
#     admin_notes = models.TextField(blank=True, null=True)
    
#     # ========== Timestamps ==========
#     order_date = models.DateTimeField(auto_now_add=True)
#     confirmed_at = models.DateTimeField(blank=True, null=True)
#     processed_at = models.DateTimeField(blank=True, null=True)
#     packed_at = models.DateTimeField(blank=True, null=True)
#     shipped_at = models.DateTimeField(blank=True, null=True)
#     delivered_at = models.DateTimeField(blank=True, null=True)
#     cancelled_at = models.DateTimeField(blank=True, null=True)
#     returned_at = models.DateTimeField(blank=True, null=True)
#     refunded_at = models.DateTimeField(blank=True, null=True)
#     updated_at = models.DateTimeField(auto_now=True)
    
#     # ========== Audit Fields ==========
#     created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='orders_created')
#     updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='orders_updated')
    
#     class Meta:
#         db_table = 'sa_order'
#         ordering = ['-order_date']
#         indexes = [
#             models.Index(fields=['order_id']),
#             models.Index(fields=['user']),
#             models.Index(fields=['status']),
#             models.Index(fields=['payment_status']),
#             models.Index(fields=['order_date']),
#         ]
    
#     def save(self, *args, **kwargs):
#         if not self.order_id:
#             import time
#             import random
#             timestamp = int(time.time())
#             random_num = random.randint(100, 999)
#             self.order_id = f"FRV{timestamp}{random_num}"
#         super().save(*args, **kwargs)
    
#     def __str__(self):
#         return f"Order #{self.order_id} - {self.user.email}"
    
#     @property
#     def total_items(self):
#         return self.items.aggregate(total=models.Sum('quantity'))['total'] or 0
    
#     @property
#     def order_status_display(self):
#         return dict(self.ORDER_STATUS_CHOICES).get(self.status, self.status)
    
#     @property
#     def can_cancel(self):
#         """Check if order can be cancelled"""
#         return self.status in ['PENDING', 'CONFIRMED', 'PROCESSING']
    
#     @property
#     def can_return(self):
#         """Check if order can be returned (within 7 days of delivery)"""
#         from django.utils import timezone
#         if self.status == 'DELIVERED' and self.delivered_at:
#             days_since_delivery = (timezone.now() - self.delivered_at).days
#             return days_since_delivery <= 7
#         return False

from django.db import models
from django.utils import timezone
from decimal import Decimal
import uuid
import time
import random


class Order(models.Model):
    """
    Enterprise Production Level Order Model
    Amazon / Flipkart Style Architecture
    """

    # ==========================================
    # ORDER STATUS
    # ==========================================

    ORDER_STATUS_CHOICES = [

        ('PENDING', 'Pending'),

        ('CONFIRMED', 'Confirmed'),

        ('PROCESSING', 'Processing'),

        ('PACKED', 'Packed'),

        ('SHIPPED', 'Shipped'),

        ('OUT_FOR_DELIVERY', 'Out for Delivery'),

        ('DELIVERED', 'Delivered'),

        ('CANCELLED', 'Cancelled'),

        ('RETURN_REQUESTED', 'Return Requested'),

        ('RETURN_APPROVED', 'Return Approved'),

        ('RETURNED', 'Returned'),

        ('REFUNDED', 'Refunded'),
    ]

    # ==========================================
    # PAYMENT STATUS
    # ==========================================

    PAYMENT_STATUS_CHOICES = [

        ('PENDING', 'Pending'),

        ('PAID', 'Paid'),

        ('FAILED', 'Failed'),

        ('REFUNDED', 'Refunded'),

        ('UNPAID', 'Unpaid'),
    ]

    # ==========================================
    # PAYMENT METHOD
    # ==========================================

    PAYMENT_METHOD_CHOICES = [

        ('COD', 'Cash On Delivery'),

        ('STRIPE', 'Stripe'),
    ]

    # ==========================================
    # ORDER IDENTIFICATION
    # ==========================================

    order_id = models.CharField(
        max_length=30,
        unique=True,
        editable=False,
        db_index=True
    )

    tracking_number = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        db_index=True
    )

    invoice_number = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    # ==========================================
    # USER DETAILS
    # ==========================================

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='orders'
    )

    # ==========================================
    # SHIPPING DETAILS
    # ==========================================

    shipping_name = models.CharField(
        max_length=255
    )

    shipping_email = models.EmailField()

    shipping_phone = models.CharField(
        max_length=20
    )

    shipping_alternate_phone = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    shipping_address_line1 = models.TextField()

    shipping_address_line2 = models.TextField(
        blank=True,
        null=True
    )

    shipping_landmark = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    shipping_city = models.CharField(
        max_length=100
    )

    shipping_state = models.CharField(
        max_length=100
    )

    shipping_pincode = models.CharField(
        max_length=20
    )

    shipping_country = models.CharField(
        max_length=100,
        default='India'
    )

    # ==========================================
    # BILLING DETAILS
    # ==========================================

    same_as_shipping = models.BooleanField(
        default=True
    )

    billing_name = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    billing_address = models.TextField(
        blank=True,
        null=True
    )

    billing_city = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    billing_state = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    billing_pincode = models.CharField(
        max_length=20,
        blank=True,
        null=True
    )

    # ==========================================
    # PRICE DETAILS
    # ==========================================

    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00")
    )

    discount_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00")
    )

    coupon_code = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    coupon_discount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00")
    )

    shipping_charge = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00")
    )

    tax_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00")
    )

    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0.00")
    )

    # ==========================================
    # PAYMENT DETAILS
    # ==========================================

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES
    )

    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='PENDING',
        db_index=True
    )

    payment_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        db_index=True
    )

    stripe_session_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        db_index=True
    )

    payment_response = models.JSONField(
        blank=True,
        null=True
    )

    payment_failure_reason = models.TextField(
        blank=True,
        null=True
    )

    payment_completed_at = models.DateTimeField(
        blank=True,
        null=True
    )

    # ==========================================
    # PAYMENT EXPIRY
    # ==========================================

    payment_expiry = models.DateTimeField(
        blank=True,
        null=True
    )

    is_payment_expired = models.BooleanField(
        default=False
    )

    # ==========================================
    # ORDER STATUS
    # ==========================================

    status = models.CharField(
        max_length=30,
        choices=ORDER_STATUS_CHOICES,
        default='PENDING',
        db_index=True
    )

    order_note = models.TextField(
        blank=True,
        null=True
    )

    admin_notes = models.TextField(
        blank=True,
        null=True
    )

    cancel_reason = models.TextField(
        blank=True,
        null=True
    )

    cancelled_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='cancelled_orders'
    )

    # ==========================================
    # DELIVERY DETAILS
    # ==========================================

    estimated_delivery_date = models.DateField(
        blank=True,
        null=True
    )

    delivered_to = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    # ==========================================
    # TIMESTAMPS
    # ==========================================

    order_date = models.DateTimeField(
        auto_now_add=True,
        db_index=True
    )

    confirmed_at = models.DateTimeField(
        blank=True,
        null=True
    )

    processed_at = models.DateTimeField(
        blank=True,
        null=True
    )

    packed_at = models.DateTimeField(
        blank=True,
        null=True
    )

    shipped_at = models.DateTimeField(
        blank=True,
        null=True
    )

    delivered_at = models.DateTimeField(
        blank=True,
        null=True
    )

    cancelled_at = models.DateTimeField(
        blank=True,
        null=True
    )

    returned_at = models.DateTimeField(
        blank=True,
        null=True
    )

    refunded_at = models.DateTimeField(
        blank=True,
        null=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    # ==========================================
    # AUDIT FIELDS
    # ==========================================

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='orders_created'
    )

    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders_updated'
    )

    # ==========================================
    # META
    # ==========================================

    class Meta:

        db_table = 'sa_order'

        ordering = ['-order_date']

        indexes = [

            models.Index(fields=['order_id']),

            models.Index(fields=['user']),

            models.Index(fields=['status']),

            models.Index(fields=['payment_status']),

            models.Index(fields=['payment_method']),

            models.Index(fields=['order_date']),

            models.Index(fields=['tracking_number']),

            models.Index(fields=['payment_id']),
        ]

    # ==========================================
    # SAVE METHOD
    # ==========================================

    def save(self, *args, **kwargs):

        if not self.order_id:

            timestamp = int(time.time())

            random_num = random.randint(1000, 9999)

            self.order_id = (
                f"FRV{timestamp}{random_num}"
            )

        super().save(*args, **kwargs)

    # ==========================================
    # STRING REPRESENTATION
    # ==========================================

    def __str__(self):

        return (
            f"Order #{self.order_id} "
            f"- {self.user.email}"
        )

    # ==========================================
    # TOTAL ITEMS
    # ==========================================

    @property
    def total_items(self):

        return (
            self.items.aggregate(
                total=models.Sum('quantity')
            )['total'] or 0
        )

    # ==========================================
    # DISPLAY STATUS
    # ==========================================

    @property
    def order_status_display(self):

        return dict(
            self.ORDER_STATUS_CHOICES
        ).get(
            self.status,
            self.status
        )

    # ==========================================
    # CANCEL CHECK
    # ==========================================

    @property
    def can_cancel(self):

        return self.status in [

            'PENDING',

            'CONFIRMED',

            'PROCESSING'
        ]

    # ==========================================
    # RETURN CHECK
    # ==========================================

    @property
    def can_return(self):

        if (
            self.status == 'DELIVERED'
            and self.delivered_at
        ):

            days_since_delivery = (
                timezone.now() -
                self.delivered_at
            ).days

            return days_since_delivery <= 7

        return False

    # ==========================================
    # PAYMENT EXPIRY CHECK
    # ==========================================

    @property
    def is_expired(self):

        if (
            self.payment_expiry
            and timezone.now() >
            self.payment_expiry
        ):

            return True

        return False

    # ==========================================
    # MARK PAYMENT FAILED
    # ==========================================

    def mark_payment_failed(
        self,
        reason=None
    ):

        self.payment_status = 'FAILED'

        self.payment_failure_reason = reason

        self.save()

    # ==========================================
    # MARK PAYMENT SUCCESS
    # ==========================================

    def mark_payment_success(
        self,
        payment_id=None
    ):

        self.payment_status = 'PAID'

        self.payment_id = payment_id

        self.payment_completed_at = (
            timezone.now()
        )

        self.status = 'CONFIRMED'

        self.confirmed_at = (
            timezone.now()
        )

        self.save()

    # ==========================================
    # CANCEL ORDER
    # ==========================================

    def cancel_order(
        self,
        reason=None,
        user=None
    ):

        self.status = 'CANCELLED'

        self.cancel_reason = reason

        self.cancelled_by = user

        self.cancelled_at = (
            timezone.now()
        )

        self.save()



class OrderItem(models.Model):
    """Order Items Model"""
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    
    # Snapshot of product details at order time
    product_name = models.CharField(max_length=255)
    product_image = models.CharField(max_length=500, blank=True, null=True)
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount_percentage = models.IntegerField(default=0)
    
    # Order item details
    quantity = models.IntegerField()
    size = models.CharField(max_length=20, blank=True, null=True)
    color = models.CharField(max_length=50, blank=True, null=True)
    
    # Return/Refund details
    is_return_requested = models.BooleanField(default=False)
    return_reason = models.TextField(blank=True, null=True)
    return_status = models.CharField(max_length=50, blank=True, null=True)
    return_requested_at = models.DateTimeField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'sa_order_item'
    
    @property
    def subtotal(self):
        return self.product_price * self.quantity
    
    def __str__(self):
        return f"{self.quantity} x {self.product_name}"


class OrderTracking(models.Model):
    """Order Tracking History (Like courier tracking)"""
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='tracking_history')
    status = models.CharField(max_length=50)
    location = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'sa_order_tracking'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.order.order_id} - {self.status} - {self.created_at}"


class Coupon(models.Model):
    """Coupon/Discount Model"""

    DISCOUNT_TYPE_CHOICES = [
        ('PERCENTAGE', 'Percentage'),
        ('FIXED', 'Fixed Amount'),
    ]

    code = models.CharField(max_length=50, unique=True)

    title = models.CharField(max_length=255)

    description = models.TextField(blank=True, null=True)

    discount_type = models.CharField(
        max_length=20,
        choices=DISCOUNT_TYPE_CHOICES
    )

    discount_value = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    min_order_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    max_discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    # Usage limits
    usage_limit = models.IntegerField(default=1)

    used_count = models.IntegerField(default=0)

    per_user_limit = models.IntegerField(default=1)

    # Validity
    valid_from = models.DateTimeField()

    valid_to = models.DateTimeField()

    is_deleted = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_stackable = models.BooleanField(default=False)

    # Applicable products/categories
    applicable_products = models.ManyToManyField(
        Product,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'sa_coupon'

    def __str__(self):
        return self.code

    def is_valid(self):
        from django.utils import timezone

        return (
            not self.is_deleted and
            self.valid_from <= timezone.now() <= self.valid_to and
            self.used_count < self.usage_limit
        )
    

class Notify_Admin(models.Model):

    order = models.ForeignKey(
        "Order",
        on_delete=models.CASCADE,
        related_name="admin_notifications"
    )

    title = models.CharField(
        max_length=255
    )

    message = models.TextField()

    is_read = models.BooleanField(
        default=False
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        db_table = "notify_admin"
        ordering = ["-id"]

    def __str__(self):
        return f"{self.title} - {self.order.order_id}"