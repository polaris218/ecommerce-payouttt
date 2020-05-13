import stripe

from api.models import BidPayment
from accounts.Dwolla_payment_management import DwollaPayment
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


class StripePayment(object):

    def bid_payment(self, bid, request):
        payment_token = eval(request.user.stripe_payment_method).get('token').get('id')
        charge = stripe.Charge.create(
            amount=int(bid.bid_amount * 100),
            currency='usd',
            description=bid.product_to_bid_on.title,
            source=payment_token,
        )
        if charge:
            admin_funding_source = DwollaPayment().get_admin_account_funding_resource()
            bid.paid = True
            bid.save()
            bid_payment = BidPayment.objects.create(amount=bid.bid_amount,
                                                    admin_url=admin_funding_source,
                                                    buyer_url=charge.to_dict().get('receipt_url'),
                                                    success_url=charge.to_dict().get('receipt_url')
                                                    , bid=bid,
                                                    payment_method=BidPayment.STRIPE)
            return bid_payment
        return None

    def get_customer(self, user):
        if not user.stripe_customer_id:
            user.stripe_customer_id = stripe.Customer.create()['id']
            user.save()
        return user.stripe_customer_id

    def get_customer_secret(self, user):
        intent = stripe.SetupIntent.create(
            customer=self.get_customer(user)
        )
        return intent.client_secret
