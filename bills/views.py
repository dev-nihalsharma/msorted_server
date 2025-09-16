
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
import requests

from bills.services import fetch_bills_from_eko
from server.utils import required_data, resp_fail, resp_success
import random
from datetime import datetime, timedelta


class BillsAPI(viewsets.ModelViewSet):

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'])
    def fetch_bills(self, request, *args, **kwargs):

        data = request.data
        required_data([
            "bill_operators"
            "source_ip",
            "latlong"
        ], data)

        source_ip = data['source_ip']
        latlong = data['latlong']

        if len(data['bill_operators']) == 0:
            return Response(resp_fail("No bill operators found."))

        bills_data = []

        for op in data['bill_operators']:
            payload = {
                "source_ip": source_ip,
                "utility_acc_no": op['utilityAccNo'],
                "confirmation_mobile_no": op['phoneNumber'],
                "sender_name": op['registeredName'],
                "operator_id": op['operatorId'],
                "latlong": latlong
            }

            res = fetch_bills_from_eko(payload)['data']

            bill_data = {'amount': res['amount'], 'due_date': res['billDueDate'],
                         'biller_name': op['operatorName'], 'customer_name': res['utilitycustomername'], 'id': random.randint(1000, 9999)}

            bills_data.append(bill_data)

        print("Data", bills_data)

        return Response(resp_success(data=bills_data, message="Bills fetched successfully"))

    @action(detail=False, methods=['post'])
    def pay_bill(self, request, *args, **kwargs):
        # Placeholder for paying bills logic
        return Response(resp_fail(message="Pay bill functionality is not implemented yet."))
