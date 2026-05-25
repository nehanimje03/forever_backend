# Standard Library Imports
from datetime import timedelta, datetime
from django.utils import timezone
from sqlite3 import IntegrityError
import jwt

# Django Imports
from django.contrib.auth import authenticate
from django.db import transaction
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.hashers import make_password,check_password
from rest_framework_simplejwt.settings import api_settings as jwt_settings
from rest_framework_simplejwt.tokens import RefreshToken
from django.db.models import Q

# Project Imports
from authentication.models import *
from utils.api.core_utils import *
from utils.api.error_code import *
from utils.notificaion.notification_service import *
from utils.notificaion.send_mail_html_format import *
from .serializers import *


