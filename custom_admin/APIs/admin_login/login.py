from ...views import *  



class AdminLoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            email = request.data.get('email', '').lower()
            password = request.data.get('password')

            missing = check_missing_fields(request.data, ['email', 'password'])
            if missing:
                return missing

            user = authenticate(request, email=email, password=password)

            if not user:
                return Response({'status': 'fail','message': f'{BAD_REQUEST} - Invalid email or password'}, 
                                status=status.HTTP_401_UNAUTHORIZED)

            if not user.is_active:return Response({'status': 'fail','message': 'Account is disabled. Contact administrator.'}, 
                                                  status=status.HTTP_403_FORBIDDEN)

            if not user.is_staff:
                return Response({'status': 'fail','message': 'Access denied. Admin privileges required.'}, 
                                status=status.HTTP_403_FORBIDDEN)

            tokens = get_tokens_for_user(user)
            
            user.last_login = timezone.now()
            user.save(update_fields=['last_login'])

            response_data = {
                'status': 'success',
                'message': f'{SUCCESS} - Admin login successfully',
                'data': {
                    'access_token': tokens['access'],
                    'refresh_token': tokens['refresh'],
                    'user': {
                        'id': user.id,
                        'email': user.email,
                        'name': user.get_full_name() or user.username,
                        'is_staff': user.is_staff,
                        'is_superuser': user.is_superuser
                    }
                }
            }
            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'status': 'error','message': f'{INTERNAL_SERVER_ERROR} - Internal server error: {str(e)}'}, 
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)