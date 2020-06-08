from django.core.mail import send_mail as main_email_send
from django.conf import settings

from accounts.models import User
from api.models import Bid, Product
from django.template.loader import get_template


class Email(object):

    def send_email(self, subject, content, user, html_content=None):
        main_email_send(subject, content, settings.EMAIL_HOST_USER, [user.email], fail_silently=False,
                        html_message=html_content)

    def send_bulk_email(self, subject, content, user_emails, html_content=None):
        main_email_send(subject, content, settings.EMAIL_HOST_USER, user_emails, fail_silently=False,
                        html_message=html_content)

    def send_welcome_email(self, user):
        htmly = get_template('email_template.html')
        d = {'email_body': 'Welcome to Payouttt, you can now buy and sell products.',
             "email_type": "Welcome to Payouttt"}
        html_content = htmly.render(d)
        self.send_email('Welcome to Payouttt', '', user, html_content=html_content)

    def send_buyer_email(self, bid):
        htmly = get_template('email_template.html')
        d = {'email_body': 'You have successfully pay for the product, we will email more details',
             "email_type": "Successful Payment", "user": bid.user}
        html_content = htmly.render(d)
        self.send_email('Successful Payment', '', bid.user, html_content=html_content)

    def send_seller_email(self, bid):
        htmly = get_template('email_template.html')
        d = {'email_body': 'Admin successfully pay for the items.',
             "email_type": "Successful Payment", "user": bid.product_to_bid_on.seller}
        html_content = htmly.render(d)
        self.send_email('Successful Payment', '', bid.product_to_bid_on.seller, html_content=html_content)

    def send_email_to_seller(self, bid):
        htmly = get_template('email_template.html')
        content = 'Somebody bid on your product'
        items = [
            {"name": "Product Name", "value": bid.product_to_bid_on.title},
            {"name": "Size", "value": '{}|{}'.format(bid.shoe_size.shoe_size, bid.shoe_size.country)},
            {"name": "Bid Value", "value": '${}'.format(bid.bid_amount)},
        ]
        d = {'email_body': content,
             "email_type": 'Congratulations Somebody Bid', 'items': items, "user": bid.product_to_bid_on.seller}
        html_content = htmly.render(d)
        self.send_email('Congratulations Somebody Bid', '', bid.product_to_bid_on.seller, html_content=html_content)
        self.send_email_to_bidder(bid)
        self.send_email_to_all_buyers(bid)

    def send_product_email_to_seller(self, product):
        listing_price = product.listing_price
        processing_fee = round((listing_price / 100) * 1, 2)
        transaction_fee = round((listing_price / 100) * 3, 2)
        listing_price = listing_price - processing_fee - transaction_fee
        content = 'Successfully Listed product.'
        size = product.shoe_sizes.all().first()
        items = [
            {"name": "Product Name", "value": product.title},
            {"name": "Size", "value": '{}|{}'.format(size.shoe_size, size.country) if size else ''},
            {"name": "Listing Price", "value": '${}'.format(product.listing_price)},
            {"name": "Processing Fee", "value": '${}'.format(processing_fee)},
            {"name": "Transaction Fee", "value": '${}'.format(transaction_fee)},
            {"name": "Total Payouttt", "value": '${}'.format(round(listing_price, 2))},
        ]
        htmly = get_template('email_template.html')

        d = {'email_body': content,
             "email_type": 'Successfully Listed a product', 'items': items, "user": product.seller}
        html_content = htmly.render(d)

        self.send_email('Successfully Listed a product', '', product.seller, html_content=html_content)
        self.send_email_to_higher_ask(product)

    def send_email_to_all_buyers(self, bid):
        all_users = Bid.objects.filter(product_to_bid_on=bid.product_to_bid_on, shoe_size=bid.shoe_size,
                                       bid_amount__lt=bid.bid_amount).values_list('user__email', flat=True)
        content = 'Somebody bid Higher than you'
        htmly = get_template('email_template.html')

        items = [
            {"name": "Product Name", "value": bid.product_to_bid_on.title},
            {"name": "Size", "value": '{}|{}'.format(bid.shoe_size.shoe_size, bid.shoe_size.country)},
            {"name": "Bid Value", "value": '${}'.format(bid.bid_amount)},
        ]

        d = {'email_body': content,
             "email_type": 'Somebody bid higher', 'items': items}
        html_content = htmly.render(d)

        self.send_bulk_email("Somebody bid higher", '', all_users, html_content=html_content)

    def send_email_to_bidder(self, bid):
        htmly = get_template('email_template.html')
        content = 'Congratulations your bid is live'
        items = [
            {"name": "Product Name", "value": bid.product_to_bid_on.title},
            {"name": "Size", "value": '{}|{}'.format(bid.shoe_size.shoe_size, bid.shoe_size.country)},
            {"name": "Bid Value", "value": '${}'.format(bid.bid_amount)},
            {"name": "Shipping", "value": '${}'.format(15)},
            {"name": "Total", "value": '${}'.format(15 + int(bid.bid_amount))},
        ]
        d = {'email_body': content,
             "email_type": 'Congratulations your bid is live', 'items': items, "user": bid.user}
        html_content = htmly.render(d)
        self.send_email('Congratulations your bid is live', '', bid.user, html_content=html_content)

    def send_email_to_higher_ask(self, product):
        users = Product.objects.filter(sku_number=product.sku_number, listing_price__gt=product.listing_price,
                                       shoe_sizes__in=product.shoe_sizes.all()).values_list('seller',
                                                                                            flat=True).exclude(
            seller=product.seller).distinct()
        for user in User.objects.filter(id__in=set(users)):
            shoe_size = product.shoe_sizes.all().first()
            if shoe_size:
                htmly = get_template('email_template.html')
                content = 'Someone placed a new lowest ask'
                items = [
                    {"name": "Product Name", "value": product.title},
                    {"name": "Size", "value": '{}|{}'.format(shoe_size.shoe_size, shoe_size.country)},
                    {"name": "Listing Price", "value": '${}'.format(product.listing_price)},
                    {"name": "Product SKU", "value": product.sku_number},
                ]
                d = {'email_body': content,
                     "email_type": 'Someone placed a new lowest ask', 'items': items, "user": user}
                html_content = htmly.render(d)
                self.send_email('Someone placed a new lowest ask', '', user, html_content=html_content)
