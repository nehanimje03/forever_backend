# Standard Library
import os
import random
from datetime import datetime, timedelta
from twilio.rest import Client
import re
import jwt

# Third-Party
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import BasePermission

# Django Imports
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage
from rest_framework_simplejwt.tokens import RefreshToken,AccessToken

# Local Project Imports
from utils.api.error_code import *



def check_missing_fields(request, required_fields, source="data"):
    if source == "params":
        data_source = request.query_params
    else:
        data_source = request

    missing = [field for field in required_fields if not data_source.get(field)]
    if missing:
        return Response({'status': 'fail','message': f'{BAD_REQUEST} - Missing fields: {", ".join(missing)}'}, 
                        status=status.HTTP_400_BAD_REQUEST)
    return None


class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.is_superuser
        )
    
    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)
    

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    access = AccessToken.for_user(user)
    
    if user.is_staff or user.is_superuser:
        refresh.set_exp(lifetime=timedelta(days=30))
        access.set_exp(lifetime=timedelta(days=30))
    else:
        refresh.set_exp(lifetime=timedelta(days=7))
        access.set_exp(lifetime=timedelta(days=7))    
    return {
        'refresh': str(refresh),
        'access': str(access),
    }



def random_otp(length=6):
    return ''.join([str(random.randint(0, 9)) for _ in range(length)])


def create_access_token_for_password_reset(user_id, email):
    expire_time = datetime.utcnow() + timedelta(minutes=15)
    
    payload = {
        "user_id": user_id,
        "email": email,
        "type": "password_reset",
        "exp": expire_time,
        "iat": datetime.utcnow(),
    }
    token = jwt.encode(payload,settings.JWT_SECRET_KEY,algorithm=settings.JWT_ALGORITHM)
    return token


def validate_pagination_fields(request):
    errors = []

    page_number = request.data.get('page_number')
    page_size = request.data.get('page_size')

    if page_number is None:
        errors.append("page_number")
    if page_size is None:
        errors.append("page_size")

    if errors:
        return Response(
            {
                "status": "fail",
                "message": f"Missing fields: {', '.join(errors)}"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        page_number = int(page_number)
        page_size = int(page_size)
    except (ValueError, TypeError):
        return Response(
            {
                "status": "fail",
                "message": "page_number and page_size must be integers"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    if page_number <= 0 or page_size <= 0:
        return Response(
            {
                "status": "fail",
                "message": "page_number and page_size must be greater than 0"
            },
            status=status.HTTP_400_BAD_REQUEST
        )

    return page_number, page_size


def paginate_queryset(queryset, page_number, page_size):
    paginator = Paginator(queryset, page_size)
    if paginator.count == 0:
        return Response({
            "status": "success",
            "message": "No records found",
            "data": {
                "total_items": 0,
                "total_pages": 0,
                "current_page": page_number,
                "results": []
            }
        }, status=status.HTTP_200_OK)

    try:
        page_obj = paginator.page(page_number)
    except EmptyPage:
        return Response({
            "status": "fail",
            "message": "Requested page does not exist",
            "data": {}
        }, status=status.HTTP_404_NOT_FOUND)

    return page_obj, paginator


def integer_field_validator(request, fields, source="data"):
    if hasattr(request, "query_params"):
        request_obj = request
    else:
        request_obj = None

    if source == "params":
        data_source = request_obj.query_params if request_obj else request
    else:
        data_source = request_obj.data if request_obj else request

    for field in fields:
        value = data_source.get(field)

        if value is None or value == '':
            continue

        if field in ['contact_no', 'contact_number', 'alternate_contact_number']:
            if not re.fullmatch(r'[6-9]\d{9}', str(value)):
                return Response({
                    "status": "fail",
                    "message": f"{BAD_REQUEST} - {field} must be a valid 10-digit mobile number starting with 6–9"
                }, status=status.HTTP_400_BAD_REQUEST)
            continue
        try:
            int(value)
        except (ValueError, TypeError):
            return Response({
                "status": "fail",
                "message": f"{BAD_REQUEST} - {field} must be a valid integer."
            }, status=status.HTTP_400_BAD_REQUEST)

    return None


def image_files_type_validator(request, required_fields):
    for field in required_fields:
        file = request.FILES.get(field)

        if not file:
            continue

        if not hasattr(file, 'name'):
            return Response({"status": "fail","message": f"{BAD_REQUEST} - Invalid file for {field}."},status=status.HTTP_400_BAD_REQUEST)
        
        max_size = 5 * 1024 * 1024 
        if file.size > max_size:
            return Response({"status": "fail", "message": f"{BAD_REQUEST} - File size should be less than 5MB."}, status=status.HTTP_400_BAD_REQUEST)

        file_type = file.name.split('.')[-1].lower()
        if file_type not in ['png', 'jpg', 'jpeg']:
            return Response({"status": "fail", "message": f"{BAD_REQUEST} - Only png, jpg, jpeg files are allowed." }, status=status.HTTP_400_BAD_REQUEST)

    return None


def send_whatsapp_message(mobile, message):
    try:
        mobile = (str(mobile).replace(" ", "").replace("+91", ""))
        client = Client(settings.TWILIO_ACCOUNT_SID,settings.TWILIO_AUTH_TOKEN)

        client.messages.create(
            body=message,
            from_=settings.TWILIO_WHATSAPP_NUMBER,
            to=f"whatsapp:+91{mobile}"
        )
        return True

    except Exception as e:
        return False