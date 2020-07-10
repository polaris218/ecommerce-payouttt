from django.db import models

from accounts.models import User
from api.models import Product


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True


class Package(BaseModel):
    title = models.CharField(max_length=100)
    products = models.ManyToManyField(Product, null=True, blank=True)
    sold = models.BooleanField(default=False)
    retail_price = models.FloatField(default=0)
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    listing_price = models.FloatField()
    image = models.FileField(null=True, blank=True)

    def __str__(self):
        return self.title
