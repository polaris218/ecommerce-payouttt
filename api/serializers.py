from rest_framework import serializers
from . import models


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Product
        fields = ('id', 'seller', 'title', 'sku_number', 'colorway', 'shoe_size', 'brand', 'listing_price',
                  'url', 'release_date', 'total_sales', 'type', 'image', 'sold',)


class BidPaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.BidPayment
        exclude = ('id',)


class BidSerializer(serializers.ModelSerializer):
    can_pay = serializers.SerializerMethodField()
    product = serializers.SerializerMethodField()
    bid_payment = serializers.SerializerMethodField()

    class Meta:
        model = models.Bid
        fields = ('id', 'product_to_bid_on', 'user', 'bid_amount', 'shoe_size', 'can_pay', 'product', 'bid_payment')

        extra_kwargs = {"verified_account": {"read_only": True}}

    def get_can_pay(self, obj):
        if obj.product_to_bid_on.listing_price <= obj.bid_amount:
            return True
        return False

    def get_bid_payment(self, obj):
        bid_payment = obj.bidpayment_set.all().order_by('-id').first()
        return BidPaymentSerializer(bid_payment, many=False).data

    def get_product(self, obj):
        return ProductSerializer(obj.product_to_bid_on, many=False).data


class VerifySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.VerifiedUserApplication
        fields = ('payouttt_username', 'email_address',)


class SellerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Seller
        fields = (
            'seller', 'full_name', 'email_address', 'phone_number', 'verified_account', 'street_address', 'city',
            'state',
            'zip_code',)

        extra_kwargs = {"verified_account": {"read_only": True},
                        "full_name": {"write_only": True},
                        "email_address": {"write_only": True},
                        'street_address': {"write_only": True},
                        'phone_number': {"write_only": True},
                        'city': {"write_only": True},
                        'state': {"write_only": True},
                        'zip_code': {"write_only": True}
                        }


class FeaturedSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.FeaturedProduct
        fields = ('featured',)

        extra_kwargs = {"featured": {"read_only": True}}
        depth = 1


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Feedback
        fields = ('email', 'feedback',)


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ContactUs
        fields = ('email', 'subject', 'question',)

        extra_kwargs = {"email": {"write_only": True},
                        "subject": {"write_only": True},
                        "question": {"write_only": True}}
