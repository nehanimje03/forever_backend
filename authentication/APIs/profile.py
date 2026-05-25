from ..views import *


class UserProfileAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            serializer = UserProfileSerializer(request.user)
            response_data = {
                'status': 'success',
                'data': serializer.data
            }
            return Response(response_data, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({"status": "error","message": f"{INTERNAL_SERVER_ERROR} - Internal Server Error: {str(e)}"}, 
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)        

    
    def put(self, request):
        try:
            serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()

                response_data = {
                    'status': 'success',
                    'message': f'{SUCCESS} - Profile updated successfully',
                    'data': serializer.data
                }
                return Response(response_data, status=status.HTTP_200_OK)
            
            return Response({'status': 'fail','errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            return Response({"status": "error","message": f"{INTERNAL_SERVER_ERROR} - Internal Server Error: {str(e)}"}, 
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
