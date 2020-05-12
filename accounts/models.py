from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _

from accounts.managers import CustomUserManager
from localflavor.us.us_states import STATE_CHOICES
from phonenumber_field.modelfields import PhoneNumberField


class User(AbstractUser):
    SELLER = 'seller'
    BUYER = 'buyer'
    USER_TYPES = (
        (SELLER, 'Seller'),
        (BUYER, 'Buyer'),
    )

    username = None
    email = models.EmailField(_('email address'), unique=True)
    full_name = models.CharField(max_length=100, null=True, blank=True)
    phone_number = PhoneNumberField(null=True, blank=True)
    verified_account = models.BooleanField(default=False)
    street_address = models.CharField(max_length=120, null=True, blank=True)
    city = models.CharField(max_length=120, null=True, blank=True)
    state = models.CharField(max_length=2, choices=STATE_CHOICES, null=True, blank=True)
    zip_code = models.IntegerField(default=0)
    business_name = models.CharField(max_length=120, null=True, blank=True)
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default=SELLER)
    dwolla_customer_id = models.CharField(max_length=255, null=True, blank=True)
    dwolla_customer_url = models.URLField(max_length=255, null=True, blank=True)
    master_account_url = models.URLField(max_length=255, null=True, blank=True)
    ssn = models.CharField(max_length=50, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    stripe_customer_id = models.CharField(max_length=250, null=True, blank=True)
    stripe_payment_method = models.CharField(max_length=2000, null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    def get_fund_source(self):
        return self.fundingsource_set.all().order_by('-id').first()


class FundingSource(models.Model):
    name = models.CharField(max_length=100, default='', blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    source_url = models.URLField()

    def __str__(self):
        return str(self.id)
