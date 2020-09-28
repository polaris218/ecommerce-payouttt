from django.db import models
from django.contrib.auth.models import AbstractUser

from accounts.models import User
from api.models import Bid


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=False)

    class Meta:
        abstract = True


class FeedbackModel(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.email


class AdminTransaction(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bid = models.ForeignKey(Bid, on_delete=models.CASCADE)
    paid = models.BooleanField(default=False)
    transfer_id = models.CharField(max_length=100, null=True, blank=True)
    stripe_error = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    amount = models.FloatField()

    def __str__(self):
        return self.user.email
