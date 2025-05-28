from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status

from authentication.models import OTP

User = get_user_model()
USER_PASSWORD_FOR_NEW_SIGNUPS = "123456"


@pytest.mark.django_db(databases=['default', 'replica'], transaction=True)
class TestSignupView:
    def test_signup_success(self, client, mocker):
        mock_send_sms = mocker.patch('authentication.views.send_sms_task.delay')
        url = reverse("signup")
        phone_to_signup = "+123456789"
        data = {
            "phone_number": phone_to_signup,
            "password": USER_PASSWORD_FOR_NEW_SIGNUPS,
            "repeat_password": USER_PASSWORD_FOR_NEW_SIGNUPS,
            "first_name": "New",
            "last_name": "User",
            "date_of_birth": "1995-05-10",
        }

        response = client.post(url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED, 'wrong status code'
        assert User.objects.filter(phone_number=phone_to_signup).exists(), "User hasn't been created"
        new_user = User.objects.get(phone_number=phone_to_signup)
        assert not new_user.is_verified, "the user shouldn't be verified"
        assert "authUser" in response.data["data"], 'authUser not in data'
        assert response.data["data"]["authUser"]["phone_number"] == phone_to_signup, 'phone number has changed'
        assert OTP.objects.filter(user=new_user).exists(), "otp doesn't exist"
        otp_instance = OTP.objects.get(user=new_user)
        mock_send_sms.assert_called_once_with(phone_to_signup, f"Your verification code is {otp_instance.code}. ")

    def test_signup_invalid_data(self, client):
        url = reverse("signup")
        data = {
            "phone_number": "+19876543211",
            "password": "12345",  # Invalid
            "repeat_password": "12345",
            "first_name": "New",
            "last_name": "User",
            "date_of_birth": "1995-05-10",
        }
        response = client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "password" in response.data["errors"] or "non_field_errors" in response.data["errors"]

    def test_signup_password_mismatch(self, client):
        url = reverse("signup")
        data = {
            "phone_number": "+19876543212",
            "password": USER_PASSWORD_FOR_NEW_SIGNUPS,
            "repeat_password": "mismatchedpassword",
            "first_name": "Mismatch",
            "last_name": "User",
            "date_of_birth": "1995-05-10",
        }
        response = client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "repeat_password" in response.data["errors"] or "non_field_errors" in response.data["errors"]


@pytest.mark.django_db(databases=['default', 'replica'], transaction=True)
class TestLoginView:
    def test_login_success_verified_user(self, client, test_user_a):
        url = reverse("login")
        data = {"phone_number": test_user_a.phone_number, "password": "123456"}
        response = client.post(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert "authUser" in response.data["data"]
        assert "access_token" in response.data["data"]
        assert "refresh_token" in response.data["data"]
        assert response.data["data"]["authUser"]["phone_number"] == test_user_a.phone_number

    def test_login_unverified_user(self, client, test_unverified_user, db):
        url = reverse("login")
        data = {"phone_number": test_unverified_user.phone_number, "password": '123456'}
        response = client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["success"] is False
        assert "User not verified" in response.data["message"]

    def test_login_invalid_credentials(self, client, test_user_a):
        url = reverse("login")
        data = {"phone_number": test_user_a.phone_number, "password": "wrongpassword"}
        response = client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["success"] is False
        assert "Invalid credentials" in response.data['message']

    def test_login_inactive_user(self, client, test_inactive_user, db):
        url = reverse("login")
        data = {"phone_number": test_inactive_user.phone_number, "password": '123456'}
        response = client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data["success"] is False
        assert "Invalid credentials" in response.data["message"]


@pytest.mark.django_db(databases=['default', 'replica'], transaction=True)
class TestVerifyPhoneNumberView:
    def test_verify_phone_success(self, client, db):
        user_to_verify_phone = "+19997776661"
        user_to_verify_password = "123456"
        user = User.objects.create_user(
            phone_number=user_to_verify_phone,
            password=user_to_verify_password,
            first_name="ToVerify",
            last_name="User",
            is_verified=False,
            date_of_birth='1990-01-01',
        )
        otp_instance = OTP.objects.create(user=user)

        url = reverse("verify_phone_number")
        data = {"phone_number": user.phone_number, "code": otp_instance.code}

        response = client.post(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert "authUser" in response.data['data']
        assert "access_token" in response.data['data']
        user.refresh_from_db()
        assert user.is_verified == True
        otp_instance.refresh_from_db()
        assert otp_instance.is_used == True

    def test_verify_phone_invalid_otp(self, client, db):
        user_to_verify_phone = "+19997776661"
        user_to_verify_password = "123456"
        user = User.objects.create_user(
            phone_number=user_to_verify_phone,
            password=user_to_verify_password,
            first_name="ToVerify",
            last_name="User",
            is_verified=False,
            date_of_birth='1990-01-01',
        )
        OTP.objects.create(user=user, code="111222")  # A valid OTP for this user

        url = reverse("verify_phone_number")
        data = {"phone_number": user.phone_number, "code": "000000"}  # Incorrect code

        response = client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid or expired OTP" in response.data["message"]
        user.refresh_from_db()
        assert not user.is_verified

    def test_verify_phone_expired_otp(self, client, db, mocker):
        user_to_verify_phone = "+19997776661"
        user_to_verify_password = "123456"
        user = User.objects.create_user(
            phone_number=user_to_verify_phone,
            password=user_to_verify_password,
            first_name="ToVerify",
            last_name="User",
            is_verified=False,
            date_of_birth='1990-01-01',
        )
        otp_instance = OTP.objects.create(user=user)
        otp_instance.expires_at = timezone.now() - timedelta(minutes=6)  # Set OTP to expired
        otp_instance.save()

        url = reverse("verify_phone_number")
        data = {"phone_number": user.phone_number, "code": otp_instance.code}
        response = client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Invalid or expired OTP" in response.data["message"]
        user.refresh_from_db()
        assert not user.is_verified

    # test_user_a is already verified
    def test_verify_phone_already_verified_user(self, client, test_user_a, db):
        OTP.objects.create(user=test_user_a, code="555666")
        url = reverse("verify_phone_number")
        data = {"phone_number": test_user_a.phone_number, "code": "555666"}

        response = client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "User already verified" in response.data["message"]

    def test_verify_phone_user_not_found(self, client):
        url = reverse("verify_phone_number")
        data = {"phone_number": "+10000000000", "code": "123123"}
        response = client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "User not found" in response.data["message"]


@pytest.mark.django_db(databases=['default', 'replica'], transaction=True)
class TestForgotPasswordView:
    def test_forgot_password_success(self, client, test_user_a, mocker):
        mock_send_sms = mocker.patch('authentication.views.send_sms_task.delay')
        url = reverse("forgot_password")
        data = {"phone_number": test_user_a.phone_number}

        response = client.post(url, data, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert OTP.objects.filter(user=test_user_a, is_used=False).exists()
        mock_send_sms.assert_called_once()

    def test_forgot_password_inactive_user(self, client, test_inactive_user, db, mocker):
        mock_send_sms = mocker.patch('authentication.views.send_sms_task.delay')
        url = reverse("forgot_password")
        data = {"phone_number": test_inactive_user.phone_number}
        response = client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "User not found" in response.data["message"]
        mock_send_sms.assert_not_called()


@pytest.mark.django_db(databases=['default', 'replica'], transaction=True)
class TestSendOTPView:
    # user_a_client is authenticated with test_user_a (verified, active)
    def test_send_otp_success_authenticated_user(self, user_a_client, test_user_a, mocker):
        mock_send_sms = mocker.patch('authentication.views.send_sms_task.delay')
        url = reverse("send_otp")

        response = user_a_client.post(url, {}, format="json")
        assert response.status_code == status.HTTP_200_OK

        assert OTP.objects.filter(user=test_user_a).exists()
        mock_send_sms.assert_called_once()

    # client is unauthenticated
    def test_send_otp_unauthenticated_user(self, client):
        url = reverse("send_otp")
        response = client.post(url, {}, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_send_otp_inactive_authenticated_user(
        self, client, db, inactive_user_client, mocker
    ):  # Use unauth client, create user
        mock_send_sms = mocker.patch('authentication.views.send_sms_task.delay')
        url = reverse("send_otp")
        response = inactive_user_client.post(url, {}, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "this account has been deleted" in response.data["errors"][0]["message"]
        mock_send_sms.assert_not_called()


@pytest.mark.django_db(databases=['default', 'replica'], transaction=True)
class TestResetPasswordView:
    # user_a_client is authenticated with test_user_a
    def test_reset_password_success(self, user_a_client, test_user_a, db):
        if not hasattr(OTP, 'objects'):
            pytest.skip("OTP model not available")
        otp_code_val = "777888"
        otp_instance = OTP.objects.create(user=test_user_a, code=otp_code_val)
        new_password = "newStrongPassword123"

        url = reverse("reset_password")
        data = {
            "code": otp_instance.code,
            "password": new_password,
            "repeat_password": new_password,
        }
        response = user_a_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_200_OK
        assert response.data["success"] is True
        assert "Password reset successfully" in response.data["message"]

        test_user_a.refresh_from_db()
        assert test_user_a.check_password(new_password)
        otp_instance.refresh_from_db()
        assert otp_instance.is_used is True

    def test_reset_password_invalid_otp_code_format(self, user_a_client):
        url = reverse("reset_password")
        data = {"code": "short", "password": "newpassword", "repeat_password": "newpassword"}
        response = user_a_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "OTP must be a 6-digit number" in response.data["errors"][0]["message"]

    def test_reset_password_otp_does_not_exist(self, user_a_client, test_user_a):
        if not hasattr(OTP, 'objects'):
            pytest.skip("OTP model not available")
        url = reverse("reset_password")
        data = {
            "code": "000000",
            "password": "newpassword123",
            "repeat_password": "newpassword123",
        }
        # Ensure no OTP with code "000000" exists for this user
        OTP.objects.filter(user=test_user_a, code="000000").delete()
        response = user_a_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "OTP does not exist" in response.data["errors"][0]["message"]

    def test_reset_password_otp_expired(self, user_a_client, test_user_a, db, mocker):
        if not hasattr(OTP, 'objects'):
            pytest.skip("OTP model not available")
        otp_code_val = "999000"
        # Create OTP. Its created_at will be timezone.now()
        otp_instance = OTP.objects.create(user=test_user_a, code=otp_code_val)

        # Simulate time passing for OTP.is_valid() check by patching timezone.now()
        otp_instance.expires_at = timezone.now() - timedelta(minutes=6)
        otp_instance.save()

        url = reverse("reset_password")
        data = {
            "code": otp_instance.code,
            "password": "654321",
            "repeat_password": "654321",
        }
        response = user_a_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "OTP has expired" in response.data["errors"][0]["message"]

        test_user_a.refresh_from_db()
        assert test_user_a.check_password('123456')

    def test_reset_password_password_mismatch(self, user_a_client, test_user_a, db):
        if not hasattr(OTP, 'objects'):
            pytest.skip("OTP model not available")
        OTP.objects.create(user=test_user_a, code="123789")
        url = reverse("reset_password")
        data = {
            "code": "123789",
            "password": "newpassword123",
            "repeat_password": "anotherpassword456",
        }
        response = user_a_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Passwords do not match" in response.data["message"]

    def test_reset_password_unauthenticated(self, client):
        url = reverse("reset_password")
        response = client.post(url, {}, format="json")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db(databases=['default', 'replica'], transaction=True)
class TestUsersListView:
    def test_list_users_as_admin(self, admin_client, admin_user, test_user_a, test_user_b):
        url = reverse("users_list")
        response = admin_client.get(url)
        assert response.status_code == status.HTTP_200_OK

        phone_numbers_in_response = [user['phone_number'] for user in response.data['data']['results']]
        assert admin_user.phone_number in phone_numbers_in_response
        assert test_user_a.phone_number in phone_numbers_in_response
        assert test_user_b.phone_number in phone_numbers_in_response
        assert response.data['data']['count'] >= 3

    def test_list_users_as_non_admin(self, user_a_client):
        url = reverse("users_list")
        response = user_a_client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_create_user_as_admin_success(self, admin_client):
        url = reverse("users_list")
        new_phone = "+17778889999"
        data = {
            "phone_number": new_phone,
            "password": USER_PASSWORD_FOR_NEW_SIGNUPS,
            "first_name": "AdminCreated",
            "last_name": "SpecialUser",
            "date_of_birth": "2000-01-01",
        }
        response = admin_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(phone_number=new_phone).exists()
        new_user = User.objects.get(phone_number=new_phone)
        assert new_user.is_verified is True

    def test_create_user_as_non_admin(self, user_a_client):
        url = reverse("users_list")
        data = {
            "phone_number": "+17778889900",
            "password": USER_PASSWORD_FOR_NEW_SIGNUPS,
            "first_name": "NonAdminAttempt",
            "date_of_birth": "2000-01-01",
        }
        response = user_a_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db(databases=['default', 'replica'], transaction=True)
class TestAdminUserDetailView:
    def test_admin_retrieve_user_detail_success(self, admin_client, test_user_a):
        url = reverse("user_detail", kwargs={"pk": test_user_a.pk})
        response = admin_client.get(url)
        assert response.status_code == status.HTTP_200_OK

        user_data = response.data.get('data', response.data)  # Handle UnifiedResponse or direct
        assert user_data["phone_number"] == test_user_a.phone_number

    def test_admin_retrieve_non_existent_user(self, admin_client):
        url = reverse("user_detail", kwargs={"pk": 99999})
        response = admin_client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_admin_update_user_detail_success(self, admin_client, test_user_a):
        url = reverse("user_detail", kwargs={"pk": test_user_a.pk})
        new_first_name = "AdminUpdatedName"
        data = {"first_name": new_first_name, "is_verified": False}

        response = admin_client.patch(url, data, format="json")
        assert response.status_code == status.HTTP_200_OK

        test_user_a.refresh_from_db()
        assert test_user_a.first_name == new_first_name
        assert test_user_a.is_verified is False

    def test_admin_destroy_user_detail_success(self, admin_client, test_user_a):
        url = reverse("user_detail", kwargs={"pk": test_user_a.pk})
        response = admin_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT

        refreshed_user = User.objects.get(pk=test_user_a.pk)
        assert refreshed_user.is_active is False

    def test_user_detail_access_by_non_admin(self, user_a_client, test_user_b):
        url = reverse("user_detail", kwargs={"pk": test_user_b.pk})
        response = user_a_client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN
