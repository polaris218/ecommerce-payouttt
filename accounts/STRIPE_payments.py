import stripe

from api.models import BidPayment
from accounts.Dwolla_payment_management import DwollaPayment
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


class StripePayment(object):

    def bid_payment(self, bid, request):
        if request.method == 'POST':
            charge = stripe.Charge.create(
                amount=bid.bid_amount * 100,
                currency='usd',
                description=bid.product_to_bid_on.title,
                source=request.POST['stripeToken']
            )
            if charge:
                admin_funding_source = DwollaPayment().get_admin_account_funding_resource()
                bid.paid = True
                bid.save()
                bid_payment = BidPayment.objects.create(amount=bid.bid_amount,
                                                        admin_url=admin_funding_source,
                                                        buyer_url=charge.to_dict().get('receipt_url'),
                                                        success_url=charge.to_dict().get('receipt_url'), bid=bid,
                                                        payment_method=BidPayment.STRIPE)
                return bid_payment
        return None
