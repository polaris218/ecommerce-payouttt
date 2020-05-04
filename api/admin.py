from django.contrib import admin
from . import models

# Register your models here.
admin.site.register(models.Product)
admin.site.register(models.Bid)

admin.site.register(models.VerifiedUserApplication)
admin.site.register(models.VerifiedSellerApplication)

admin.site.register(models.ShoeSize)
admin.site.register(models.Seller)

admin.site.register(models.FeaturedProduct)
admin.site.register(models.Feedback)

admin.site.register(models.ContactUs)
