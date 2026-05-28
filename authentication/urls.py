# django Imports
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

# Local Project Imports
from .APIs.profile import *
from .APIs.login import *
from .APIs.address import * 

urlpatterns = [
    path('signup/', SignUpAPIView.as_view()),
    path('login/', LoginAPIView.as_view()),
    path('refresh-token', TokenRefreshView.as_view()),
    path('request-reset-password/', RequestResetPasswordAPIView.as_view()),
    path('verify-otp/', VerifyOTPAPIView.as_view()),
    path('reset-password/', ResetPasswordAPIView.as_view()),

    # user profile
    path('get-profile/', UserProfileAPIView.as_view()),
    path('update-profile/', UserProfileAPIView.as_view()),

    # Address
    path('create-address/', AddressApiView.as_view()),
    path('get-address/', AddressApiView.as_view()),
    path('update-address/', AddressApiView.as_view()),
    path('remove-address/', AddressApiView.as_view()),
    path('set-default-addresses/', AddressApiView.as_view()),


]
