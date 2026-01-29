from django.shortcuts import render
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework import viewsets
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from .serializers import UserSerializer
from rest_framework import status
from django.contrib.auth import authenticate
from rest_framework.views import APIView
# Create your views here.


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'id'


    def get_permissions(self):
        if self.action in ['create_user']:
            return [AllowAny()]
        elif self.action in ['me']:
            return [IsAuthenticated()]
        return [IsAdminUser()]

    @action(detail=False, methods=['get'], url_path='me')
    def me(self, request):
        user = request.user
        serializer = self.get_serializer(user)

        return Response(serializer.data)
        

    @action(detail=False, methods=['post'], url_path='create_user' )
    def create_user(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # JWT Token generation
            refresh = RefreshToken.for_user(user)

            return Response({
                "message": "User created successfully",
                "accsess": str(refresh.access_token),
                "refresh": str(refresh)
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """email + password login and JWT token generate
    """


    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        user = authenticate(request, email=email, password=password)
        if user is None:
            return Response({"error": "Invalid email or password"}, status=status.HTTP_401_UNAUTHORIZED)


        # JWT Token generation
        refresh = RefreshToken.for_user(user)
        return Response({
            "access": str(refresh.access_token),
            "refresh": str(refresh), 
            "user": {
                "id": user.id,
                "email": user.email
            }
        }, status=status.HTTP_200_OK)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]


    def post(self, request):

        try:
            refresh_token = request.data['refresh']
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Successfully logged out",
            
            }, status=status.HTTP_205_RESET_CONTENT)
        
        except Exception as e:
            return Response({'error': "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)




