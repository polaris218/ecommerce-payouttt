from plaid import Client

from django.conf import settings

from accounts.Dwolla_payment_management import DwollaPayment
from accounts.STRIPE_payments import StripePayment
from accounts.models import Plaid

import stripe

from django.conf import settings

from api.models import BidPayment

stripe.api_key = settings.STRIPE_SECRET_KEY


class PalidPayments(object):

    def __init__(self):
        self.client = Client(client_id=settings.PLAID_CLIENT_ID, secret=settings.PLAID_SECRET,
                             public_key=settings.PLAID_PUBLIC_KEY, environment=settings.PLAID_ENVIRONMENT)

    def exchange_token(self, user, public_token, account_id):
        if public_token and account_id:
            try:
                exchange_token_response = self.client.Item.public_token.exchange(public_token)
                access_token = exchange_token_response['access_token']
                item_id = exchange_token_response['item_id']
                user_plaid = Plaid.objects.filter(user=user).first()
                if not user_plaid:
                    user_plaid = Plaid.objects.create(user=user, access_token=access_token, item_id=item_id,
                                                      account_id=account_id)
                else:
                    StripePayment().get_customer(user)
                    user_plaid.access_token = access_token
                    user_plaid.item_id = item_id
                    user_plaid.account_id = account_id
                    user_plaid.save()
                return user_plaid, None
            except Exception as ex:
                return None, {"message": ex.message}
        else:
            return None, {"message": "public_token and account_id can't be empty"}

    def pay_for_order(self, bid, request):
        user_plaid = Plaid.objects.filter(user=request.user).first()
        if user_plaid and user_plaid.account_id and user_plaid.access_token:
            response = self.client.Processor.stripeBankAccountTokenCreate(user_plaid.access_token,
                                                                          user_plaid.account_id)
            if response.get('stripe_bank_account_token'):
                charge = stripe.Charge.create(amount=int((bid.product_to_bid_on.listing_price + 15) * 100), currency='usd',
                                              source=response.get('stripe_bank_account_token'),
                                              description=bid.product_to_bid_on.title)
                if charge:
                    admin_funding_source = DwollaPayment().get_admin_account_funding_resource()
                    bid.paid = True
                    bid.save()
                    bid_payment = BidPayment.objects.create(amount=bid.product_to_bid_on.listing_price + 15,
                                                            admin_url=admin_funding_source,
                                                            buyer_url=charge.to_dict().get('receipt_url'),
                                                            success_url=charge.to_dict().get('receipt_url')
                                                            , bid=bid,
                                                            payment_method=BidPayment.PLAID)
                    return bid_payment
        return None
    # self.client.Processor.stripeBankAccountTokenCreate(access_token, 'x1BpKv7zb4FXBaLBa9LnI4vaAAajK6fnRxvBQ')
    # def create_admin_plaid_receipent(self, user):

    # addres = {"street": ["96 Guild Street", "9th Floor"], "city": "London", "postal_code": "SE14 8JW", "country": "GB"}
    # client.PaymentInitiation.create_recipient("Wonder Wallet", 'GB29NWBK60161331926819', address)

# Get all accounts
# response = client.Accounts.get(access_token)
# accounts = response['accounts']
