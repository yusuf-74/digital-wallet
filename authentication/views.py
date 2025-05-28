from django.contrib.auth import authenticate
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from core.base.views import (
    UnifiedResponseListCreateAPIView,
    UnifiedResponseRetrieveUpdateDestroyAPIView,
)
from utils.common_tasks import send_sms_task
from utils.orm_utils import query_optimizer

from .models import OTP, User
from .serializers import (
    ForgotPasswordSerializer,
    LoginResponseSerializer,
    LoginSerializer,
    ResetPasswordSerializer,
    SignupSerializer,
    UserSerializer,
)


class SignupView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        tags=['User Operations'],
        description='Register New User',
        methods=['post'],
        request=SignupSerializer,
        responses={200: ''},
    )
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Generate OTP for phone verification
            otp_code = OTP.objects.create(user=user)
            otp_code.save()
            verify_phone_number_message = f"Your verification code is {otp_code.code}. "

            send_sms_task.delay(user.phone_number, verify_phone_number_message)
            return Response(
                {
                    'success': True,
                    'message': 'User created successfuly',
                    'data': {
                        'authUser': UserSerializer(user).data,
                    },
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(
            {'success': False, 'message': 'Validation Issue', 'errors': serializer._errors},
            status=status.HTTP_400_BAD_REQUEST,
        )


class LoginView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        tags=['User Operations'],
        description='Login User',
        methods=['post'],
        request=LoginSerializer,
        responses={200: LoginResponseSerializer},
    )
    def post(self, request):
        phone_number = request.data.get('phone_number')
        password = request.data.get('password')
        user = authenticate(phone_number=phone_number, password=password)
        if user is None:
            return Response(
                {
                    'success': False,
                    'message': 'Invalid credentials',
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not user.is_verified:
            return Response(
                {
                    'success': False,
                    'message': 'User not verified',
                    'errors': [
                        {'field': 'phone_number', 'error': 'User not verified, please verify your phone number first.'}
                    ],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        refresh = RefreshToken.for_user(user)

        return Response(
            {
                'success': True,
                'message': 'Logged in successfuly',
                'data': {
                    'authUser': UserSerializer(user).data,
                    'refresh_token': str(refresh),
                    'access_token': str(refresh.access_token),
                },
            },
            status=status.HTTP_200_OK,
        )


class VerifyPhoneNumberView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        tags=['User Operations'],
        description='Verify Phone Number',
        methods=['post'],
        responses={200: LoginResponseSerializer},
    )
    def post(self, request):
        phone_number = request.data.get('phone_number')
        otp_code = request.data.get('code')
        try:
            user = User.objects.get(phone_number=phone_number, is_active=True)
            if not user.is_verified:
                try:
                    otp = OTP.objects.get(user=user, code=otp_code)
                except OTP.DoesNotExist:
                    return Response(
                        {
                            'success': False,
                            'message': 'Invalid or expired OTP',
                            'errors': [{'field': 'code', 'message': 'OTP is invalid or has expired'}],
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                if otp.is_valid():
                    user.is_verified = True
                    user.save()
                    otp.mark_as_used()
                    token = RefreshToken.for_user(user)
                    data = UserSerializer(user).data
                    return Response(
                        {
                            'success': True,
                            'message': 'Phone number verified successfully',
                            'data': {
                                'authUser': data,
                                'refresh_token': str(token),
                                'access_token': str(token.access_token),
                            },
                        },
                        status=status.HTTP_200_OK,
                    )
                else:
                    return Response(
                        {
                            'success': False,
                            'message': 'Invalid or expired OTP',
                            'errors': [{'field': 'code', 'message': 'OTP is invalid or has expired'}],
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            return Response(
                {
                    'success': False,
                    'message': 'User already verified',
                    'errors': [{'field': 'phone_number', 'message': 'this account is already verified'}],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except User.DoesNotExist:
            return Response(
                {
                    'success': False,
                    'message': 'User not found',
                    'errors': [{'field': 'phone_number', 'message': 'this account does not exist or has been deleted'}],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


class ForgotPasswordView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    @extend_schema(
        tags=['User Operations'],
        description='Forgot Password',
        methods=['post'],
        request=ForgotPasswordSerializer,
        responses={200: ''},
    )
    def post(self, request):
        phone_number = request.data.get('phone_number')
        user = User.objects.filter(phone_number=phone_number).first()

        if user:
            if not user.is_active:
                return Response(
                    {
                        'success': False,
                        'message': 'User not found',
                        'errors': [
                            {
                                'field': 'phone_number',
                                'message': 'this account has been deleted',
                            }
                        ],
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            otp_code = OTP.objects.create(user=user)
            otp_code.save()

            reset_password_message = f""" Hello {user.first_name},\n
                You have requested to reset your password. Please use the following OTP code to reset your password: {otp_code.code}.\n
                """
            send_sms_task.delay(user.phone_number, reset_password_message)

            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_400_BAD_REQUEST)


class SendOTPView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['User Operations'],
        description='Send OTP for Phone Verification',
        methods=['post'],
        responses={200: ''},
    )
    def post(self, request):
        user = request.user
        if not user.is_active:
            return Response(
                {
                    'success': False,
                    'message': 'User not found',
                    'errors': [{'field': 'user', 'message': 'this account has been deleted'}],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        otp_code = OTP.objects.create(user=user)
        otp_code.save()
        send_sms_task.delay(user.phone_number, f"Your verification code is {otp_code.code}.")
        return Response(status=status.HTTP_200_OK)


class ResetPasswordView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['User Operations'],
        description='Reset Password',
        methods=['post'],
        request=ResetPasswordSerializer,
        responses={200: ''},
    )
    def post(self, request):
        otp_code = request.data.get('code')
        if not otp_code or not otp_code.isdigit() or len(otp_code) != 6:
            return Response(
                {
                    'success': False,
                    'message': 'Invalid OTP',
                    'errors': [{'field': 'otp', 'message': 'OTP must be a 6-digit number'}],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:

            otp = OTP.objects.get(user=request.user, code=otp_code)
            if otp.is_valid():
                password = request.data.get('password')
                repeat_password = request.data.get('repeat_password')
                if password != repeat_password:
                    return Response(
                        {
                            'success': False,
                            'message': 'Passwords do not match',
                            'errors': [{'field': 'password', 'message': 'Passwords do not match'}],
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                try:
                    user = User.objects.get(id=request.user.id)
                    user.set_password(password)
                    user.save()
                    otp.mark_as_used()
                    return Response(
                        {
                            'success': True,
                            'message': 'Password reset successfully',
                        },
                        status=status.HTTP_200_OK,
                    )
                except User.DoesNotExist:
                    return Response(
                        {
                            'success': False,
                            'message': 'User not found',
                            'errors': [{'field': 'user', 'message': 'this account with '}],
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            else:
                return Response(
                    {
                        'success': False,
                        'message': 'OTP expired',
                        'errors': [{'field': 'otp', 'message': 'OTP has expired, please request a new one'}],
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except OTP.DoesNotExist:
            return Response(
                {
                    'success': False,
                    'message': 'Invalid OTP',
                    'errors': [{'field': 'code', 'message': 'OTP does not exist'}],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )


@extend_schema(tags=['User Operations'])
class UserDetailView(UnifiedResponseRetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    lookup_field = None

    def get_queryset(self):
        return query_optimizer(User, self.request)

    def get_object(self):
        user = User.objects.get(id=self.request.user.id)
        if not user.is_active:
            raise User.DoesNotExist
        return user

    def retrieve(self, request, *args, **kwargs):
        user = self.get_object()
        if not user.is_active:
            return Response(
                {
                    'success': False,
                    'message': 'User not found',
                    'errors': [{'field': 'user', 'message': 'this account has been deleted'}],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            {
                'success': True,
                'message': 'User retrieved successfully',
                'data': UserSerializer(user).data,
            },
            status=status.HTTP_200_OK,
        )

    def update(self, request):
        user = User.objects.get(id=request.user.id)
        if not user.is_active:
            return Response(
                {'error': 'this account has been deleted'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        request.data.pop('is_verified', None)
        return super().update(request)

    def destroy(self, request):
        user = User.objects.get(id=request.user.id)
        if not user.is_active:
            return Response(
                {
                    'success': False,
                    'message': 'User not found',
                    'errors': [{'field': 'user', 'message': 'this account has been deleted'}],
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        user.is_active = False
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(tags=['User Operations'])
class UsersListView(UnifiedResponseListCreateAPIView):
    permission_classes = [IsAdminUser]
    serializer_class = UserSerializer

    def get_queryset(self):
        return query_optimizer(User, self.request)

    def create(self, request, *args, **kwargs):
        request.data['is_verified'] = True
        user = super().create(request, *args, **kwargs)
        return Response(user.data, status=status.HTTP_201_CREATED)


@extend_schema(tags=['User Operations'])
class AdminUserDetailView(UnifiedResponseRetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = False
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
