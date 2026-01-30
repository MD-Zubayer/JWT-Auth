
from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
    
)
from rest_framework.routers import DefaultRouter
from users.views import UserViewSet, LoginView, LogoutView, ForgotPasswordView, ResetPasswordView

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('users/', include('jwtauth.users.urls')),
    path('api/', include(router.urls)),
    path('api/login/', LoginView.as_view(), name='login'),
    path("api/logout/", LogoutView.as_view(), name="logout"),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # path('api/verify-email/', VerifyEmailView.as_view(), name='token_verify'),
    path('api/forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path("api/reset-password/", ResetPasswordView.as_view(), name="reset-password")
]
