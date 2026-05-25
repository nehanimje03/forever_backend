from ..views import *


class SignUpAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            username = request.data.get('username')
            email = request.data.get('email').lower()
            password = request.data.get('password')

            missing = check_missing_fields(request.data, ['username', 'email', 'password'])
            if missing:
                return missing

            if CustomUser.objects.filter(username=username).exists():
                return Response({'status': 'fail','message': f'{BAD_REQUEST} - Username already exists'}, 
                                status=status.HTTP_400_BAD_REQUEST)

            if CustomUser.objects.filter(email=email).exists():
                return Response({'status': 'fail','message': f'{BAD_REQUEST} - Email already exists'}, 
                                status=status.HTTP_400_BAD_REQUEST)

            with transaction.atomic():
                user = CustomUser.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                )

            subject, body = construct_email_welcome(user.username, email)
            send_emails(config, email, subject, body)

            response_data = {
                'status': 'success',
                'message': f'{SUCCESS} - Account created successfully',
                'data': {
                    'user': {
                        'id': user.id,
                        'email': user.email,
                        'name': user.username
                    }
                }
            }
            return Response(response_data, status=status.HTTP_201_CREATED)

        except IntegrityError:
            return Response({"status": "fail","message": f"{BAD_REQUEST} - Username or Email already exists"}, 
                            status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"status": "error","message": f"{INTERNAL_SERVER_ERROR} - Internal server error: {str(e)}"}, 
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            email = request.data.get('email').lower()
            password = request.data.get('password')

            missing = check_missing_fields(request.data,['email', 'password'])
            if missing:
                return missing

            user = authenticate(request,email=email,password=password)
            if not user:
                return Response({'status': 'fail','message': f'{BAD_REQUEST} - Email or Password is incorrect'}, 
                                status=status.HTTP_400_BAD_REQUEST)

            if not user.is_active:
                return Response({'status': 'fail','message': 'Account is inactive'}, 
                                status=status.HTTP_403_FORBIDDEN)

            tokens = get_tokens_for_user(user)

            response_data = {
                'status': 'success',
                'message': f'{SUCCESS} - User Login successfully.',
                'data': {
                    'access_token': tokens['access'],
                    'refresh_token': tokens['refresh'],
                    'user': {
                        'id': user.id,
                        'email': user.email,
                        'name': user.username                    
                    }
                }
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"status": "error","message": f"{INTERNAL_SERVER_ERROR} - Internal server error: {str(e)}"}, 
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RequestResetPasswordAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            email = request.data.get('email').lower()

            missing = check_missing_fields(request.data, ['email'])
            if missing:
                return missing

            user = CustomUser.objects.get(email__iexact=email)

            otp = str(random_otp(6))

            user.verify_code = make_password(otp)
            user.verify_code_expire_at = timezone.now() + timedelta(minutes=10)
            user.save(update_fields=['verify_code', 'verify_code_expire_at'])

            config = SMTPMail.objects.filter(is_deactive=False).first()

            if not config:
                return Response({"status": "fail", "message": f"{BAD_REQUEST} - SMTP configuration not found"},
                                status=status.HTTP_400_BAD_REQUEST)

            subject, body = construct_email_forgot_password(email, otp)
            send_emails(config, email, subject, body)

            response_data = {
                "status": "success",
                "message": f"{SUCCESS} - OTP sent successfully",
                "data": {"otp_expiry_minutes": 10}
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except CustomUser.DoesNotExist:
            return Response({"status": "fail", "message": f"{NOT_FOUND} - User does not exist"},status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({"status": "error", "message": f"{INTERNAL_SERVER_ERROR} - Internal server error: {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class VerifyOTPAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            email = request.data.get('email').lower()
            otp = request.data.get('otp')

            missing = check_missing_fields(request.data, ['email', 'otp'])
            if missing:
                return missing

            user = CustomUser.objects.get(email__iexact=email)

            if not user.verify_code:
                return Response({"status": "fail", "message": f"{BAD_REQUEST} - OTP not generated"},status=status.HTTP_400_BAD_REQUEST)

            if timezone.now() > user.verify_code_expire_at:
                return Response({"status": "fail", "message": f"{BAD_REQUEST} - OTP expired"},status=status.HTTP_400_BAD_REQUEST)

            if not check_password(otp, user.verify_code):
                return Response({"status": "fail", "message": f"{BAD_REQUEST} - Invalid OTP"},status=status.HTTP_400_BAD_REQUEST)

            return Response({"status": "success","message": f"{SUCCESS} - OTP verified"}, status=status.HTTP_200_OK)

        except CustomUser.DoesNotExist:
            return Response({"status": "fail", "message": f"{NOT_FOUND} - User does not exist"},status=status.HTTP_404_NOT_FOUND)
        

class ResetPasswordAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            email = request.data.get('email').lower()
            new_password = request.data.get('new_password')
            confirm_password = request.data.get('confirm_password')

            missing = check_missing_fields(request.data, ['email', 'new_password', 'confirm_password'])
            if missing:
                return missing

            if new_password != confirm_password:
                return Response({"status": "fail", "message": f"{BAD_REQUEST} - Password mismatch"},status=status.HTTP_400_BAD_REQUEST)

            user = CustomUser.objects.get(email__iexact=email)
            user.set_password(new_password)

            user.verify_code = None
            user.verify_code_expire_at = None
            user.save()

            return Response({"status": "success","message": f"{SUCCESS} - Password reset successfully"}, status=status.HTTP_200_OK)

        except CustomUser.DoesNotExist:
            return Response({"status": "fail", "message": f"{NOT_FOUND} - User does not exist"},status=status.HTTP_404_NOT_FOUND)
        
        except Exception as e:
            return Response({"status": "error", "message": f"{INTERNAL_SERVER_ERROR} - Internal server error: {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

