from multiprocessing import process
import pdb
from server.constants import login_otp_message
import email
from functools import partial
import random
from savings.models import Savings
from users.models import AuthOTP, User
from server.utils import required_data, resp_fail, resp_success
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import models
from dotenv import load_dotenv
from users.serializers import UserSerializer
from twilio.rest import Client

# Load environment variables
load_dotenv()


def send_otp_sms(mobile, otp, message):

    account_sid = process.env.get('TWILIO_ACCOUNT_SID')
    auth_token = process.env.get('TWILIO_AUTH_TOKEN')
    twilio_number = process.env.get('TWILIO_PHONE_NUMBER')

    client = Client(account_sid, auth_token)

    res = client.messages.create(
        body=message.format(otp=otp),
        from_=twilio_number,
        to=mobile
    )

    if res.error_code:
        return Response(resp_fail("Failed to send OTP SMS"))


def send_otp(mobile):
    AuthOTP.objects.filter(mobile=mobile).delete()

    temp_otp = random.randint(9999, 99999)
    otp = AuthOTP(mobile=mobile, otp=temp_otp)
    otp.save()

    # send_otp_sms(mobile, temp_otp, login_otp_message)

    return Response(
        resp_success("OTP Sent Successfully!", {
            "otp": otp.otp,
            "mobile": mobile
        }))


def resend_otp(mobile):
    prev_otp = AuthOTP.objects.filter(mobile=mobile).first()

    prev_otp.attempts += 1
    prev_otp.save()

    # send_otp_sms(mobile, prev_otp, login_otp_message)
    return Response(
        resp_success("OTP Sent Successfully!", {
            "otp": prev_otp.otp,
            "mobile": mobile
        }))


def verify_otp(mobile, entered_otp, user_exists, data={}):
    otp = AuthOTP.objects.filter(mobile=mobile).first()

    if not otp:
        return Response(resp_fail("Invalid OTP"))

    attempts_left = 3 - otp.attempts

    if attempts_left <= 0:
        return Response(resp_fail("Maximum attempts reached"))

    if not otp.otp == entered_otp:
        otp.attempts += 1
        otp.save()
        return Response(resp_fail(f"Invalid OTP, {attempts_left} Attempts Left"))

    user = User.objects.filter(mobile=mobile).first()

    if not user_exists:
        # signup
        required_data(['first_name', 'last_name', 'email'], data)

        user = User.objects.create_user(username=mobile, mobile=mobile, email=data['email'],
                                        first_name=data['first_name'], last_name=data['last_name'])
        user.save()

    user_data = UserSerializer(user, partial=True).data
    token = RefreshToken.for_user(user)
    otp.delete()

    return Response(resp_success("OTP Verified Successfully!", {'user': user_data, 'access': str(token.access_token), 'refresh': str(token)}))


def fetch_bank_balance(user):
    # Placeholder function to fetch bank balance
    # In a real application, this would involve API calls to the bank's system
    # For now, we'll just return a dummy value
    return 1000.00  # Dummy balance


def get_spend_available(user):
    user_savings = Savings.objects.filter(user=user, is_completed=False)
    total_achieved = user_savings.aggregate(
        total=models.Sum('target_achieved'))['total'] or 0

    return user.total_balance - total_achieved
