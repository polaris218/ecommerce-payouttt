import shippo

from addresses.models import Address
from django.conf import settings

shippo.config.api_key = settings.SHIPPO_API_KEY
shippo.config.api_version = "2018-02-08"
shippo.config.verify_ssl_certs = True
shippo.config.rates_req_timeout = 30.0


class ShippoAddressManagement(object):

    def user_valid_address(self, user):
        return Address.objects.filter(user=user, is_valid=True).first()

    def validate_address(self, address_data):
        address_from = shippo.Address.create(
            name=address_data.get('full_name'),
            company=address_data.get('company'),
            street1=address_data.get('street1'),
            city=address_data.get('city'),
            state=address_data.get('state'),
            zip=address_data.get('zip'),
            country=address_data.get('country'),
            email=address_data.get('email'),
            validate=True,
        )
        address_validation = address_from.get("validation_results").get('is_valid')
        address_id = address_from.get("object_id")
        message = ''
        if not address_validation:
            messages = address_from.get("validation_results").get('messages')
            if messages and len(messages):
                message = messages[0].text
            else:
                message = "Not a valid address, Please try again."
        return address_validation, message, address_id

    def get_adming_address(self):
        return Address.objects.filter(admin_address=True).first()
