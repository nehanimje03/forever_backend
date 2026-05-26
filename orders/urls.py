from django.urls import path
from orders.APIs.stripe_webhook import *
from orders.APIs.coupon import *
from orders.APIs.order import *
from orders.APIs.my_orders import *
from orders.APIs.order_details import *
from orders.APIs.order_tracking import *
from orders.APIs.return_order import *

urlpatterns = [
    path('create/', CreateOrderAPIView.as_view(), name='create-order'),
    path('payment/webhook/',stripe_webhook,name='stripe_webhook'),
    path('my-orders/', MyOrdersAPIView.as_view(), name='my-orders'),
    path('order-detail/<str:order_id>/', OrderDetailAPIView.as_view(), name='order-detail'),
    path("order-cancel/", CancelOrderAPIView.as_view(), name="cancel-order"),
    path('order-tracking/<str:order_id>/', OrderTrackingAPIView.as_view(), name='order-tracking'),
    path('<str:order_id>/return', ReturnOrderAPIView.as_view(), name='return-order'),
    path('validate-coupon/', ValidateCouponAPIView.as_view()),


]