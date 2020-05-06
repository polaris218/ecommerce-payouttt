from datetime import datetime, timedelta

import dwollav2

from accounts.models import User, FundingSource
from api.models import BidPayment
from core.EmailHelper import Email

app_key = 'YPk2xm0sc79tuaC06FPAmXJK44ewlq2IaNZOgkcnXoplJykXoJ'
app_secret = 'lGsQ4WLtXKYfmFJPIpfQsQTC2RCrXZ7x6m93UWwTgKbafYqEbU'
TOKEN = 'Q8i5xgDiMDrwsiGWc1hVkjzSpNDAvFcOCtZeCQbxk7A4KxKJ12'


class DwollaPayment(object):
    def __init__(self):
        self.client = dwollav2.Client(key=app_key, secret=app_secret, environment='sandbox')
        self.app_token = self.client.Auth.client()

    def set_master_account(self, user):
        if not user.master_account_url:
            root = self.app_token.get('/')
            account_url = root.body['_links']['account']['href']
            if user.is_superuser:
                user.master_account_url = account_url
                user.save()

        funding_sources = self.app_token.get('%s/funding-sources' % user.master_account_url)
        for fund_source in funding_sources.body['_embedded']['funding-sources']:
            name = fund_source['name']
            funding_resource_url = fund_source['_links']['self']['href']
            FundingSource.objects.get_or_create(user=user, source_url=funding_resource_url, name=name)

    def get_all_customers(self):
        customers = self.app_token.get('customers', {'limit': 10})

    def create_customer(self, user):
        request_body = {
            'firstName': user.first_name,
            'lastName': user.last_name,
            'email': user.email,
            'type': 'personal',
            'ipAddress': '99.99.99.99'
        }

        # if user.user_type == User.BUYER and user.ssn:
        request_body['type'] = 'personal'
        request_body['address1'] = user.street_address
        request_body['city'] = user.city
        if not user.state:
            request_body['state'] = 'NY'
        else:
            request_body['state'] = user.state.upper()
        request_body['postalCode'] = str(user.zip_code)
        request_body['ssn'] = user.ssn
        if user.date_of_birth:
            request_body['dateOfBirth'] = user.date_of_birth.strftime('%Y-%m-%d')
        else:
            request_body['dateOfBirth'] = (datetime.now() - timedelta(days=7200)).strftime('%Y-%m-%d')

        # request_body['businessName'] = user.business_name,

        customer = self.app_token.post('customers', request_body)
        user.dwolla_customer_url = customer.headers['location']
        user.dwolla_customer_id = user.dwolla_customer_url.split('/')[-1]
        user.save()

    def get_customer_iav_token(self, user):
        if user.dwolla_customer_url:
            customer_token = self.app_token.post('%s/iav-token' % user.dwolla_customer_url)
            return customer_token.body.get('token')
        return 'Customer is not connected to Dwolla'

    def get_admin_account_funding_resource(self):
        funding_resource = FundingSource.objects.filter(user__is_superuser=True).order_by('-id').first()
        if funding_resource:
            return funding_resource.source_url
        return None

    def send_payment(self, bid):
        admin_funding_source = self.get_admin_account_funding_resource()
        if admin_funding_source:
            request_body = {
                '_links': {
                    'source': {
                        'href': bid.user.get_fund_source().source_url
                    },
                    'destination': {
                        'href': bid.product_to_bid_on.seller.get_fund_source().source_url
                    }
                },
                'amount': {
                    'currency': 'USD',
                    'value': str(bid.bid_amount)
                },
            }

            transfer = self.app_token.post('transfers', request_body)

            if transfer.status == 201:
                bid.paid = True
                bid.save()
                bid_payment = BidPayment.objects.create(amount=bid.bid_amount,
                                                        admin_url=admin_funding_source,
                                                        buyer_url=bid.user.get_fund_source().source_url,
                                                        success_url=transfer.headers['location'], bid=bid)
                try:
                    Email().send_buyer_email(bid)
                except:
                    pass
                return bid_payment
        return False

    def send_seller_payment(self, bid_payment):
        admin_funding_source = self.get_admin_account_funding_resource()
        if admin_funding_source:
            request_body = {
                '_links': {
                    'source': {
                        'href': admin_funding_source
                    },
                    'destination': {
                        'href': bid_payment.bid.product_to_bid_on.seller.get_fund_source().source_url
                    }
                },
                'amount': {
                    'currency': 'USD',
                    'value': str(bid_payment.bid.bid_amount)
                },
            }

            transfer = self.app_token.post('transfers', request_body)

            if transfer.status == 201:
                bid_payment.seller_url = bid_payment.bid.product_to_bid_on.seller.get_fund_source().source_url
                bid_payment.seller_success_url = transfer.headers['location']
                bid_payment.save()
                try:
                    Email().send_buyer_email(bid_payment.bid)
                except:
                    pass
                return bid_payment
        return False


'https://api-sandbox.dwolla.com/accounts/1550879d-617d-443e-94a4-f5a1cd17cb71'
