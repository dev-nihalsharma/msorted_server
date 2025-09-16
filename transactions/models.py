
import enum
from django.db import models


class Transactions(models.Model):
    transaction_id = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    class TransactionType(enum.Enum):
        CREDIT = 'credit'
        DEBIT = 'debit'

    transaction_type = models.CharField(
        max_length=50, choices=[(tag.value, tag.name) for tag in TransactionType]
    )

    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    user = models.ForeignKey('users.User', on_delete=models.CASCADE)

    def __str__(self):
        return f"Transaction {self.transaction_id} for {self.user.mobile} - Amount: {self.amount}"
