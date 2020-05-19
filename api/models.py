from django.db import models
from django.db.models import Max
from phonenumber_field.modelfields import PhoneNumberField
from localflavor.us.us_states import STATE_CHOICES

# Create your models here.
from accounts.models import User


class Seller(models.Model):
    seller = models.CharField(max_length=100, primary_key=True, unique=True)
    full_name = models.CharField(max_length=100)

    email_address = models.EmailField(unique=True)
    phone_number = PhoneNumberField(unique=True)
    verified_account = models.BooleanField(default=False)

    street_address = models.CharField(max_length=120)
    city = models.CharField(max_length=120)
    state = models.CharField(max_length=2, choices=STATE_CHOICES)
    zip_code = models.IntegerField()

    def __str__(self):
        return self.seller


class ShoeSize(models.Model):
    UK = 'UK'
    USA = 'USA'
    EU = 'EU'
    CM = 'CM'
    COUNTRIES_CHOICES = (
        (USA, 'USA'),
        (UK, 'UK'),
        (EU, 'EU'),
        (CM, 'CM'),
    )

    country = models.CharField(max_length=50, choices=COUNTRIES_CHOICES, default=UK)
    shoe_size = models.FloatField(default=7)

    class Meta:
        unique_together = ('country', 'shoe_size')

    def __str__(self):
        return '{}-{}'.format(self.country, str(self.shoe_size))


class Product(models.Model):
    # seller = models.ForeignKey(User, on_delete=models.CASCADE)
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=120)
    retail_price = models.FloatField(default=0)
    sku_number = models.CharField(max_length=120)
    colorway = models.CharField(max_length=120)
    shoe_sizes = models.ManyToManyField(ShoeSize, null=True, blank=True)

    brand = models.CharField(max_length=120)
    listing_price = models.FloatField()

    url = models.URLField()
    release_date = models.DateField()

    total_sales = models.IntegerField(default=0)
    type = models.CharField(max_length=120)

    image = models.FileField(null=True, blank=True)
    sold = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class VerifiedUserApplication(models.Model):
    payouttt_username = models.CharField(max_length=120)
    email_address = models.EmailField()

    def __str__(self):
        return self.payouttt_username


class VerifiedSellerApplication(models.Model):
    payouttt_username = models.CharField(max_length=120)
    email_address = models.EmailField()

    def __str__(self):
        return self.payouttt_username


class Bid(models.Model):
    product_to_bid_on = models.ForeignKey(Product, related_name='product_selection', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # Have to update this one.

    bid_amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
    verified_account = models.BooleanField(default=False)

    shoe_size = models.ForeignKey(ShoeSize, on_delete=models.CASCADE)
    paid = models.BooleanField(default=False)

    def __str__(self):
        return self.user.email

    def can_pay(self):
        if self.bid_amount >= self.product_to_bid_on.listing_price:
            return True
        return False


class FeaturedProduct(models.Model):
    db_identification = models.CharField(max_length=120)
    featured = models.ForeignKey(Product, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.db_identification


class Feedback(models.Model):
    email = models.EmailField()
    feedback = models.TextField(max_length=700)

    def __str__(self):
        return self.email


class ContactUs(models.Model):
    email = models.EmailField()
    subject = models.CharField(max_length=120)

    question = models.TextField(max_length=500)

    def __str__(self):
        return self.email


class BidPayment(models.Model):
    STRIPE = 'stripe'
    DWOLLA = 'dwolla'
    PAYMENT_METHODS = (
        (STRIPE, 'Stripe'),
        (DWOLLA, 'Dwolla'),
    )
    amount = models.FloatField()
    admin_url = models.URLField(null=True, blank=True)
    seller_url = models.URLField(null=True, blank=True)
    seller_success_url = models.URLField(null=True, blank=True)
    buyer_url = models.URLField()
    success_url = models.URLField()
    bid = models.ForeignKey(Bid, on_delete=models.CASCADE)
    purchase_tracking = models.CharField(max_length=500, null=True, blank=True)
    purchase_label = models.CharField(max_length=500, null=True, blank=True)

    seller_tracking = models.CharField(max_length=500, null=True, blank=True)
    seller_purchase_label = models.CharField(max_length=500, null=True, blank=True)

    buyer_shippo_error = models.CharField(max_length=1000, null=True, blank=True)
    seller_shippo_error = models.CharField(max_length=1000, null=True, blank=True)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHODS, default=DWOLLA)

    def __str__(self):
        return str(self.id)
