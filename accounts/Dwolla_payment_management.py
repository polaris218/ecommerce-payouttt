from datetime import datetime, timedelta

import dwollav2

from accounts.models import User, FundingSource, DwollaAccount
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

    def create_customer(self, request_data, user):
        import pdb;
        pdb.set_trace()
        try:
            user.first_name = user.first_name or request_data.get('first_name'),
            user.last_name = user.last_name or request_data.get('last_name'),
            user.save()
            request_body = {
                'firstName': request_data.get('first_name'),
                'lastName': request_data.get('last_name'),
                'email': user.email,
                'type': 'personal',
                'ipAddress': '99.99.99.99'
            }

            request_body['type'] = 'personal'
            request_body['address1'] = request_data.get('street1')
            request_body['city'] = request_data.get('city')

            request_body['state'] = request_data.get('state').upper()
            request_body['postalCode'] = str(request_data.get('postal_code'))
            request_body['ssn'] = request_data.get('ssn')
            request_body['dateOfBirth'] = request_data.get('date_of_birth')

            customer = self.app_token.post('customers', request_body)
            return True, customer.headers['location'], customer.headers['location'].split('/')[
                -1], "Customer Successffully Created"
        except Exception as e:
            return False, '', '', str(e)

    def get_customer_iav_token(self, user):
        dwolla_account = DwollaAccount.objects.filter(user=user).last()
        if dwolla_account:
            customer_token = self.app_token.post('%s/iav-token' % dwolla_account.dwolla_customer_url)
            return customer_token.body.get('token')
        return 'Customer is not connected to Dwolla'

    def get_admin_account_funding_resource(self):
        funding_resource = FundingSource.objects.filter(user__is_superuser=True).order_by('-id').first()
        if funding_resource:
            return funding_resource.source_url
        return None

    def send_payment(self, bid):
        import pdb;pdb.set_trace()
        admin_funding_source = self.get_admin_account_funding_resource()
        if admin_funding_source:
            request_body = {
                '_links': {
                    'source': {
                        'href': bid.user.get_fund_source().source_url
                    },
                    'destination': {
                        'href': admin_funding_source  # bid.product_to_bid_on.seller.get_fund_source().source_url
                    }
                },
                'amount': {
                    'currency': 'USD',
                    'value': str(int(bid.bid_amount) + 13)
                },
            }

            transfer = self.app_token.post('transfers', request_body)

            if transfer.status == 201:
                bid.paid = True
                bid.save()
                bid_payment = BidPayment.objects.create(amount=bid.bid_amount + 13,
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
