# make a serializer to return savings with a due date with value having next month of same date if current date is more than due date of current month
import pdb
from venv import create
from rest_framework import serializers
from .models import Savings
from datetime import date, datetime, timedelta
from django.utils import timezone


class SavingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Savings
        fields = '__all__'


class SavingsListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Savings
        fields = ['id', 'saving_title', 'target_amount', 'target_date',
                  'target_achieved', 'is_completed', 'monthly_contri', 'created_at']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        current_date = datetime.today()
        created_at = instance.created_at

        # Check if the current date is greater than the target date
        if current_date.day >= created_at.day:
            representation['due_date'] = datetime(
                created_at.year, current_date.month, created_at.day) + timedelta(days=30)
        else:
            representation['due_date'] = datetime(
                created_at.year, current_date.month, created_at.day)

        return representation
