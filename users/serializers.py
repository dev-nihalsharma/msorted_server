from users.models import User
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'mobile', 'first_name', 'last_name',
                  'email', 'total_balance', 'spend_available', 'is_partner']
