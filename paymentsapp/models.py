import uuid
from django.db import models
from ecommerceapp.models import Services, Courses

class Transaction(models.Model):
    id = models.AutoField(primary_key=True)
    currency = models.CharField(max_length=3, default='USD')
    checkout_id = models.CharField(max_length=100, unique=True)
    courses = models.ForeignKey(Courses, on_delete=models.CASCADE, null=True, blank=True)
    service = models.ForeignKey(Services, on_delete=models.CASCADE, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id = models.CharField(max_length=100, unique=True, default=uuid.uuid4)  # FIXED
    mpesa_code = models.CharField(max_length=20, blank=True, null=True)
    phone_number = models.CharField(max_length=15)
    status = models.CharField(max_length=15)
    timestamp = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Transaction {self.id} - {self.status}"
    


class Payment(models.Model):
    payment_id = models.CharField(max_length=100, unique=True)
    status = models.CharField(max_length=20, choices=[('approved', 'Approved'), ('failed', 'Failed')])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.payment_id} - {self.status}"














