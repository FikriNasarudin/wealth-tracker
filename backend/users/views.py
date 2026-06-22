from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from .serializers import UserSerializer, RegisterSerializer, GoogleAuthSerializer

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

class GoogleLoginView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        try:
            serializer = GoogleAuthSerializer(data=request.data)
            if serializer.is_valid():
                idinfo = serializer.validated_data['token']
                email = idinfo.get('email')
                if not email:
                    return Response({"non_field_errors": ["Google token missing email scope."]}, status=status.HTTP_400_BAD_REQUEST)
                    
                first_name = idinfo.get('given_name', '')
                last_name = idinfo.get('family_name', '')
                
                user, created = User.objects.get_or_create(email=email, defaults={
                    'username': email,
                    'first_name': first_name,
                    'last_name': last_name
                })
                
                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'user': UserSerializer(user).data
                })
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"non_field_errors": [f"Server error during Google Login: {str(e)}"]}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class UserProfileView(generics.RetrieveAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user
