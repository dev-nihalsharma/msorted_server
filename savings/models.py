from django.conf import settings
from django.db import models


class Savings(models.Model):
    saving_title = models.CharField(max_length=100)
    target_amount = models.DecimalField(max_digits=10, decimal_places=2)
    target_date = models.DateField()
    target_achieved = models.DecimalField(
        max_digits=10, decimal_places=2, default=0)
    monthly_contri = models.DecimalField(max_digits=10, decimal_places=2)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    user = models.ForeignKey('users.User', on_delete=models.CASCADE)

    def __str__(self):
        return f"Savings Plan for {self.user.mobile} - Target: {self.target_amount}"
