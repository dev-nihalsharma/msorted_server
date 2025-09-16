from calendar import month
import uuid
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from savings.models import Savings
from savings.serializers import SavingsListSerializer, SavingsSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from users.serializers import UserSerializer
from transactions.models import Transactions
from server.utils import required_data, resp_fail, resp_success


class SavingsAPI(viewsets.ModelViewSet):
    queryset = Savings.objects.all()
    serializer_class = SavingsSerializer

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return self.queryset.filter(user=user)

    def list(self, request, *args, **kwargs):
        """ List all on-goings savings """
        queryset = self.get_queryset().filter(
            user=self.request.user, is_completed=False)

        serializer = SavingsListSerializer(queryset, many=True)

        return Response(resp_success(
            message="Savings fetched successfully",
            data=serializer.data
        ))

    @action(detail=False, methods=['GET'])
    def list_all(self, request, *args, **kwargs):
        """ List all savings including completed ones """
        queryset = self.get_queryset().filter(
            user=self.request.user)
        serializer = SavingsListSerializer(queryset, many=True)

        return Response(resp_success(
            message="All Savings fetched successfully",
            data=serializer.data
        ))

    def retrieve(self, request, *args, **kwargs):
        id = kwargs.get('pk')
        saving_wallet = self.get_queryset().filter(id=id).first()

        if not saving_wallet:
            return Response(resp_fail(message="Saving Wallet not found"))

        serializer = SavingsListSerializer(saving_wallet, many=False)

        return Response(resp_success(
            message="Saving Wallet fetched successfully",
            data=serializer.data
        ))

    def create(self, request, *args, **kwargs):
        data = request.data
        user = request.user
        required_data(['saving_title', 'target_amount',
                       'target_date', 'monthly_contri'], data=data)

        if user.spend_available < int(data['monthly_contri']):
            return Response(resp_fail("Insufficient Spend Available"))

        saving_wallet = Savings(
            saving_title=data['saving_title'],
            target_amount=data['target_amount'],
            target_date=data['target_date'],
            monthly_contri=data['monthly_contri'],
            target_achieved=data['monthly_contri'],  # Initial contribution
            user=request.user
        )
        saving_wallet.save()

        # update user for spend available
        user.spend_available -= int(data['monthly_contri'])
        user.save()

        # create a transaction record
        transaction_id = str(uuid.uuid4())

        transaction = Transactions(
            transaction_id=transaction_id,
            amount=data['monthly_contri'],
            transaction_type=Transactions.TransactionType.DEBIT.value,
            description=f"Saving Wallet Created: {saving_wallet.saving_title}",
            user=request.user
        )
        transaction.save()

        saving_wallet_data = SavingsListSerializer(
            saving_wallet, many=False).data

        user_data = UserSerializer(request.user).data

        return Response(resp_success(
            message="Saving Wallet created successfully",
            data={
                "saving_wallet": saving_wallet_data,
                "user": user_data
            }
        ))

    @action(detail=False, methods=['POST'], url_path='update_savings/(?P<id>[^/.]+)')
    def update_savings(self, request, id=None, *args, **kwargs):
        data = request.data
        user = request.user

        if user.spend_available < int(data['added_amount']) if 'added_amount' in data else 0:
            return Response(resp_fail("Insufficient Spend Available"))

        saving_wallet = self.get_queryset().filter(id=id).first()

        if not saving_wallet:
            return Response(resp_fail(message="Saving Wallet not found"))
        # Update the savings record

        if 'added_amount' in data:
            saving_wallet.target_achieved += data['added_amount']
            user.spend_available -= data['added_amount']
        if 'removed_amount' in data:
            saving_wallet.target_achieved -= data['removed_amount']
            user.spend_available += data['removed_amount']
        if 'saving_title' in data:
            saving_wallet.saving_title = data['saving_title']
        if 'target_amount' in data:
            saving_wallet.target_amount = data['target_amount']
        if 'target_date' in data:
            # updating the monthly contribution
            saving_wallet.target_date = data['target_date']

        # Check if the target amount is achieved
        if saving_wallet.target_achieved >= saving_wallet.target_amount:
            saving_wallet.is_completed = True
            saving_wallet.save()

            saving_wallet_data = SavingsListSerializer(
                saving_wallet, many=False).data
            return Response(resp_success(
                message="Saving Target Achieved",
                data=saving_wallet_data
            ))

        saving_wallet.save()
        user.save()

        # Create a transaction record for the update
        transaction_id = str(uuid.uuid4())

        if 'added_amount' in data or 'removed_amount' in data:
            transaction = Transactions(
                transaction_id=transaction_id,
                amount=data['added_amount'] if 'added_amount' in data else data['removed_amount'],
                transaction_type=Transactions.TransactionType.CREDIT.value if 'added_amount' in data else Transactions.TransactionType.DEBIT.value,
                description=f"Added to Saving Wallet: {saving_wallet.saving_title}" if 'added_amount' in data else f"Removed from Saving Wallet: {saving_wallet.saving_title}",
                user=request.user
            )

            transaction.save()

        # Serialize the updated savings record
        saving_wallet_data = SavingsListSerializer(
            saving_wallet, many=False).data

        return Response(resp_success(
            message="Saving Wallet Updated",
            data=saving_wallet_data
        ))

    def destroy(self, request, *args, **kwargs):
        id = kwargs.get('pk')
        saving_wallet = self.get_queryset().filter(id=id).first()

        if not saving_wallet:
            return Response(resp_fail("Saving Wallet not found"))

        saving_wallet.delete()

        return Response(resp_success(
            "Saving Wallet deleted successfully"
        ))
