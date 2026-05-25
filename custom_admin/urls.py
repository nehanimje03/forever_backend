from django.urls import path
from custom_admin.APIs.admin_login.login import *
from custom_admin.APIs.admin_order.admin_coupon import *
from custom_admin.APIs.admin_order.admin_return_approve import *
from custom_admin.APIs.admin_order.admin_status_payment import *
from custom_admin.APIs.admin_order.orders import *
from .APIs.admin_product.product import *

urlpatterns = [
    # login admin
    path('admin/login/', AdminLoginAPIView.as_view()),

    # create admin product
    path('create-product/', ProductApiView.as_view()),
    path('get-product/', ProductApiView.as_view()),
    path('update-product/', ProductApiView.as_view()),  
    path('delete-product/', ProductApiView.as_view()),  
    path('admin/coupons/', AdminCouponListCreateAPIView.as_view(), name='admin-coupons'),
    path('admin/coupons/<int:coupon_id>/', AdminCouponDetailAPIView.as_view(), name='admin-coupon-detail'),
    path('admin-orders/', AdminOrderListAPIView.as_view(), name='admin-order-list'),
    path('admin-order-detail/<str:order_id>/', AdminOrderDetailAPIView.as_view(), name='admin-order-detail'),
    path('admin-update-order-status/<str:order_id>/', AdminUpdateOrderStatusAPIView.as_view(), name='admin-order-status'),
    path('admin-update-payment-status/<str:order_id>/', AdminUpdatePaymentStatusAPIView.as_view(), name='admin-payment-status'),
    path('admin/orders/<str:order_id>/return', AdminReturnApproveAPIView.as_view(), name='admin-return-approve'),
]




