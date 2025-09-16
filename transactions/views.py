from datetime import timedelta
from django.shortcuts import render
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.utils import timezone
from django.db.models import Sum
from django.db.models.functions import TruncDay

from .models import Transactions
from .serializers import TransactionSerializer
from server.utils import resp_success, resp_fail
from django.db.models.functions import ExtractWeek, ExtractYear
from django.db.models.functions import ExtractMonth


class TransactionsAPI(viewsets.ViewSet):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def list(self, request):
        """
        List all transactions for the authenticated user.
        """
        user = request.user
        transactions = Transactions.objects.filter(
            user=user).order_by('-created_at')
        serialized_data = TransactionSerializer(transactions, many=True)

        return Response(resp_success(
            "Transactions fetched successfully",
            serialized_data.data
        ))

    @action(detail=False, methods=['GET'])
    def transaction_records(self, request):
        """
        Return time series data of amount transaction made by user in a day, week, or month.
        Client must provide 'range' query param: 'day', 'week', or 'month'.
        """
        range_param = request.query_params.get('range')
        if range_param not in ['day', 'week', 'month']:
            return Response(resp_fail("Invalid or missing 'range' parameter. Must be 'day', 'week', or 'month'."), status=400)

        user = request.user
        now = timezone.now()

        if range_param == 'day':
            # Get the start and end times for the year
            start_time = now.replace(
                month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            end_time = now

            queryset = Transactions.objects.filter(
                user=user, created_at__gte=start_time, created_at__lte=end_time)

            # Group by day and sum the amounts
            data = queryset.annotate(period=TruncDay('created_at')).filter(transaction_type=Transactions.TransactionType.CREDIT.value).values(
                'period').annotate(total=Sum('amount')).order_by('period')

            result = [{'time': entry['period'], 'amount': entry['total']}
                      for entry in data]

        elif range_param == 'week':
            # Get the start time as the first day of the current month
            start_time = now.replace(
                day=1, hour=0, minute=0, second=0, microsecond=0)
            # End time is current time
            end_time = now

            queryset = Transactions.objects.filter(
                user=user, created_at__gte=start_time, created_at__lte=end_time)

            # Group by week number within the current month and sum the amounts
            data = queryset.annotate(
                week=ExtractWeek('created_at')
            ).filter(transaction_type=Transactions.TransactionType.CREDIT.value).values('week').annotate(total=Sum('amount')).order_by('week')

            # Get the first week number of the current month
            first_day_of_month = start_time
            first_week_number = first_day_of_month.isocalendar()[1]

            # Get the current week number
            first_transaction_week = data.first()['week'] - first_week_number

            # Create a list for all weeks in the current month with zero amounts
            all_weeks = [{'time': week, 'amount': 0}
                         for week in range(1, 5)]

            # Update the weeks that have data
            for entry in data:
                week_index = entry['week'] - first_week_number
                if 0 <= week_index < len(all_weeks):
                    all_weeks[week_index]['amount'] = entry['total']

            result = all_weeks

        elif range_param == 'month':
            # Get the start and end times for the current year
            start_time = now.replace(
                month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
            end_time = now

            queryset = Transactions.objects.filter(
                user=user, created_at__gte=start_time, created_at__lte=end_time)

            # Group by month and sum the amounts

            data = queryset.annotate(
                month=ExtractMonth('created_at')
            ).filter(transaction_type=Transactions.TransactionType.CREDIT.value).values('month').annotate(total=Sum('amount')).order_by('month')

            # Create a list for all months (1-12) with zero amounts
            all_months = [{'time': month, 'amount': 0}
                          for month in range(0, 12)]

            # Update the months that have data
            for entry in data:
                all_months[entry['month'] - 1]['amount'] = entry['total']

            result = all_months

        return Response(resp_success(
            message=f"Transaction time series for {range_param} fetched successfully",
            data=result
        ))
