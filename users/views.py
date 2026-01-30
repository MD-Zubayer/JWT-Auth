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
from datetime import datetime, timedelta, timezone
import jwt
from django.conf import settings

from users.services.email_service import send_reset_email

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
        

    @action(detail=False, methods=['post'], url_path='create_user', permission_classes=[AllowAny] )
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
            return Response({"message": "Successfully logged out"
            
            }, status=status.HTTP_205_RESET_CONTENT)
        
        except Exception as e:
            return Response({'error': "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)




class ForgotPasswordView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')

        if not email:
            return Response(
                {"error": 'Email is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:

            # security best practice

            return Response(
                {'message': 'If email exists, reset link sent'}, 
                status=status.HTTP_200_OK
            )

        #  JWT reset token
        payload = {
            'user_id': user.id, 
            'type': 'password_reset', 
            'exp': datetime.now() + timedelta(minutes=15),
        }

        token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
        if isinstance(token, bytes):
            token = token.decode("utf-8")

        reset_link = f"http://localhost:3001/reset-password?token={token}"

        # send email
        send_reset_email(user.email, reset_link)

        return Response(
           { "message": 'if email exists, reset link sent'},
           status=status.HTTP_200_OK
        )


class ResetPasswordView(APIView):
    permission_classes = [AllowAny]


    def post(self, request):
        token = request.data.get('token')
        new_password = request.data.get('new_password')

        if not token or not new_password:
            return Response({"error": "Token and password are required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])

        except jwt.ExpiredSignatureError:
            return Response({"error": "Token expired"}, status=400)
        except jwt.InvalidTokenError:
            return Response({'error': 'Invalid token'}, status=400)
        
        try:
            user = User.objects.get(id=payload['user_id'])
        
        except User.DoesNotExist:
            return Response({'error': "User not found"}, status=404)

        user.set_password(new_password)
        user.save()

        return Response({'message': "password reset successfully"}, status=200)
