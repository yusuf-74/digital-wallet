from django.contrib.auth import password_validation
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from wallets.serializers import TierSerializer, WalletSerializer

from .models import User


class UserSerializer(serializers.ModelSerializer):
    wallets = WalletSerializer(many=True, read_only=True)
    tier = TierSerializer(read_only=True)

    class Meta:
        model = User
        fields = '__all__'
        read_only_fields = ['id', 'date_joined', 'created_at']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)

    def update(self, instance, validated_data):
        if 'password' in validated_data:
            password = validated_data.pop('password')
            instance.set_password(password)
        return super().update(instance, validated_data)


class SignupSerializer(serializers.ModelSerializer):
    repeat_password = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['phone_number', 'password', 'repeat_password', 'first_name', 'last_name', 'date_of_birth']
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data):
        if data['password'] != data['repeat_password']:
            raise serializers.ValidationError('Passwords do not match')

        password_validation.validate_password(data['password'])
        numeric_validator = RegexValidator(r'^\d{6}$', _('Enter a 6-digit numeric password.'))
        try:
            numeric_validator(data['password'])
        except serializers.ValidationError:
            raise serializers.ValidationError('Password must be a 6-digit numeric value.')
        return super().validate(data)

    def create(self, validated_data):
        del validated_data['repeat_password']
        return User.objects.create_user(**validated_data)


# SERIALIZERS FOR DOCUMENTATION
class ForgotPasswordSerializer(serializers.Serializer):
    phone_number = serializers.CharField()


class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    password = serializers.CharField()


class ResetPasswordSerializer(serializers.Serializer):
    code = serializers.CharField(required=True)
    password = serializers.CharField()
    repeat_password = serializers.CharField()

    def validate(self, data):
        if data['password'] != data['repeat_password']:
            raise serializers.ValidationError('Passwords do not match')
        return data


class LoginWithGoogleSerializer(serializers.Serializer):
    credential = serializers.CharField()


class LoginResponseSerializer(serializers.Serializer):
    authUser = UserSerializer()
    access = serializers.CharField()
    refresh = serializers.CharField()
