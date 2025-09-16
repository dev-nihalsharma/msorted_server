import datetime
import re

import uuid
from rest_framework import viewsets
from rest_framework.decorators import action
from transactions.models import Transactions
from server.utils import required_data, resp_fail, resp_success
from users.serializers import UserSerializer
from users.services import fetch_bank_balance, get_spend_available, resend_otp, send_otp, verify_otp
from .models import User

from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated


class AuthAPI(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    authentication_classes = [JWTAuthentication]
    permission_classes = []

    @action(detail=False, methods=['post'])
    def send_otp(self, *args, **kwargs):
        data = self.request.data

        required_data(['mobile'], data=data)

        # Validating Mobile Number
        try:
            mobile = int(data['mobile'])

        except ValueError:
            return Response(resp_fail('Mobile number invalid'))

        if len(str(mobile)) != 10:
            return Response(resp_fail('Mobile number must be 10 digits only'))

        return send_otp(mobile)

    @action(detail=False, methods=['post'])
    def resend_otp(self, *args, **kwargs):
        data = self.request.data

        required_data(['mobile'], data=data)

        # Validating Mobile Number
        try:
            mobile = int(data['mobile'])

        except ValueError:
            return Response(resp_fail('Mobile number invalid'))

        if len(str(mobile)) != 10:
            return Response(resp_fail('Mobile number must be 10 digits only'))

        return resend_otp(mobile)

    @action(detail=False, methods=['post'])
    def verify_otp(self, *args, **kwargs):
        data = self.request.data
        required_data(['otp', 'mobile'], data)

        # Finding User
        user = User.objects.filter(mobile=data['mobile']).first()

        user_exists = user is not None

        return verify_otp(data['mobile'], data['otp'], user_exists, data)


class UserAPI(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'])
    def profile_update(self, *args, **kwargs):
        data = self.request.data
        user = self.request.user

        if not data:
            return Response(resp_fail('No data provided'))

        if 'email' in data:
            if not re.match(r"[^@]+@[^@]+\.[^@]+", data['email']):
                return Response(resp_fail('Email is invalid'))
            user.email = data['email']

        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']

        user.save()

        user_data = UserSerializer(user).data

        return Response(resp_success('Profile updated successfully', {
            'user': user_data
        }))


class AccountingAPI(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'])
    def add_from_bank(self, *args, **kwargs):
        data = self.request.data
        required_data(['bank_details'], data)

        # Validate Bank Details
        # Fetch Bank Balance from Cashfree API
        bank_balance = fetch_bank_balance(data['bank_details'])

        user = self.request.user
        user.total_balance += bank_balance

        # fetch total achieved amount of all savings  wallet of user
        user.spend_available = get_spend_available(user)

        user.save()

        # Create a transaction record
        transaction = Transactions(
            user=user,
            transaction_type='credit',
            amount=bank_balance,
            date=datetime.now(),
            description=f'{bank_balance} Added from Bank to Wallet'
        )
        transaction.save()

        return Response(resp_success('Balance added successfully'))

    @action(detail=False, methods=['post'])
    def add_balance(self, *args, **kwargs):
        data = self.request.data
        required_data(['amount'], data)

        user = self.request.user

        user.total_balance += int(data['amount'])

        # fetch total achieved amount of all savings  wallet of user
        user.spend_available = get_spend_available(user)

        user.save()

        # Create a transaction record
        transaction_id = str(uuid.uuid4())
        transaction = Transactions(
            user=user,
            transaction_id=transaction_id,
            transaction_type='credit',
            amount=int(data['amount']),
            description=f'{data["amount"]} Added to Wallet'
        )
        transaction.save()

        return Response(resp_success('Balance added successfully', {
            'total_balance': user.total_balance,
            'spend_available': user.spend_available
        }))

    @action(detail=False, methods=['post'])
    def remove_balance(self, *args, **kwargs):
        data = self.request.data
        required_data(['amount'], data)

        user = self.request.user

        if user.spend_available < int(data['amount']):
            return Response(resp_fail('Insufficient balance to remove'))

        user.total_balance -= int(data['amount'])

        # fetch total achieved amount of all savings  wallet of user
        user.spend_available = get_spend_available(user)

        user.save()

        # Create a transaction record
        transaction_id = str(uuid.uuid4())
        transaction = Transactions(
            user=user,
            transaction_id=transaction_id,
            transaction_type='debit',
            amount=int(data['amount']),
            description=f'{data["amount"]} Removed from Wallet'
        )
        transaction.save()

        return Response(resp_success('Balance removed successfully', {
            'total_balance': user.total_balance,
            'spend_available': user.spend_available
        }))

    @action(detail=False, methods=['post'])
    def reset_balance(self, *args, **kwargs):
        user = self.request.user

        user.total_balance = 0
        user.spend_available = 0

        user.save()

        return Response(resp_success('Balance reset successfully', {
            'total_balance': 0,
            'spend_available': 0
        }))
