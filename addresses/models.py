from django.db import models

from accounts.models import User
from localflavor.us.us_states import STATE_CHOICES


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_valid = models.BooleanField(default=False)

    class Meta:
        abstract = True


class Address(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    company = models.CharField(max_length=100)
    street1 = models.CharField(max_length=256)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=3, choices=STATE_CHOICES)
    zip = models.CharField(max_length=6)
    country = models.CharField(max_length=50)
    shippo_address_id = models.CharField(max_length=250, null=True, blank=True)

    def __str__(self):
        return self.company
