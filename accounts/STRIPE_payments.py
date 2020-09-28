import ast
import math

import stripe

from accounts.models import User
from api.models import BidPayment
from accounts.Dwolla_payment_management import DwollaPayment
from django.conf import settings

from core.models import AdminTransaction

stripe.api_key = settings.STRIPE_SECRET_KEY


class StripePayment(object):

    def bid_payment(self, bid, request):
        payment_method = ast.literal_eval(bid.user.stripe_payment_method)
        payment_token = payment_method.get('paymentMethod').get('setupIntent').get('payment_method')
        charge = stripe.PaymentIntent.create(
            amount=int((bid.product_to_bid_on.listing_price + 15) * 100),
            currency='usd',
            customer=request.user.stripe_customer_id,
            description=bid.product_to_bid_on.title,
            payment_method=payment_token,
            off_session=True,
            confirm=True,
        )

        if charge:
            admin_funding_source = DwollaPayment().get_admin_account_funding_resource()
            bid.paid = True
            bid.save()
            product = bid.product_to_bid_on
            product.sold = True
            product.save()
            bid_payment = BidPayment.objects.create(amount=bid.product_to_bid_on.listing_price + 15,
                                                    admin_url=admin_funding_source,
                                                    buyer_url=charge.to_dict().get('charges').get('data')[0].get(
                                                        'receipt_url'),
                                                    success_url=charge.to_dict().get('charges').get('data')[0].get(
                                                        'receipt_url')
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

    def link_paymentmethod_with_customer(self, user):
        stripe.PaymentMethod.attach(
            eval(str(user.stripe_payment_method)).get('paymentMethod', {}).get('setupIntent', {}).get('payment_method'),
            customer=user.stripe_customer_id)

    def detach_account(self, payment_id):
        stripe.PaymentMethod.detach(payment_id)

    def verify_account(self, acount_code, user):
        response = stripe.OAuth.token(grant_type='authorization_code', code=acount_code, )
        connected_account_id = response.get('stripe_user_id', None)
        if connected_account_id:
            stripe_account = User.objects.filter(id=user.id).first()
            stripe_account.stripe_account_id = connected_account_id
            stripe_account.save()

        return True

    def get_user_account(self, user):
        user = User.objects.filter(id=user.id).first()
        if user:
            try:
                stripe.Account.create_login_link(user.stripe_account_id)
                return user
            except Exception as e:
                user.stripe_account_id = None
                user.save()
        return False

    def create_login_link(self, user):
        user_account = self.get_user_account(user)

        if user_account:
            try:
                response = stripe.Account.create_login_link(user_account.stripe_account_id)
                return response.get('url')
            except Exception as e:
                user.stripe_customer_id = None
                user.save()
        return False

    def generate_url(self, redirect_url, user):
        main_url = "https://connect.stripe.com/express/oauth/authorize?redirect_uri={}&client_id={}&suggested_capabilities[]=transfers&stripe_user[email]={}".format(
            redirect_url, settings.STRIPE_CLIENT_ID, user.email)
        return main_url

    def transfer_amount(self, transaction, bid):
        if not transaction:
            transaction = AdminTransaction.objects.create(bid=bid, user=bid.product_to_bid_on.seller,
                                                          amount=bid.bid_amount)
        if not transaction.paid and bid.product_to_bid_on.seller.stripe_account_id:

            try:
                transfer = stripe.Transfer.create(
                    amount=math.ceil(bid.bid_amount * 100),
                    currency="usd",
                    destination=bid.product_to_bid_on.seller.stripe_account_id,
                )
                if transfer:
                    transaction.paid = True
                    transaction.transfer_id = transfer.id
                    transaction.save()
            except Exception as e:
                transaction.stripe_error = str(e)
                transaction.save()
        if transaction.paid:
            return True
        return False
