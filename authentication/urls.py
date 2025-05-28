from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    AdminUserDetailView,
    ForgotPasswordView,
    LoginView,
    ResetPasswordView,
    SendOTPView,
    SignupView,
    UserDetailView,
    UsersListView,
    VerifyPhoneNumberView,
)

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', LoginView.as_view(), name='login'),
    path('verify-phone/', VerifyPhoneNumberView.as_view(), name='verify_phone_number'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset_password'),
    path('request-otp/', SendOTPView.as_view(), name='send_otp'),
    path('me/', UserDetailView.as_view(), name='user_me'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', UsersListView.as_view(), name='users_list'),
    path('<int:pk>/', AdminUserDetailView.as_view(), name='user_detail'),
]
