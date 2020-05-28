from django.core.mail import send_mail
from django.conf import settings

from api.models import Bid


class Email(object):

    def send_email(self, subject, content, user):
        send_mail(subject, content, settings.EMAIL_HOST_USER, [user.email], fail_silently=False, )

    def send_bulk_email(self, subject, content, user_emails):
        send_mail(subject, content, settings.EMAIL_HOST_USER, user_emails, fail_silently=False, )

    def send_welcome_email(self, user):
        self.send_email('Welcome to Payouttt', 'Welcome to Payouttt, you can now buy and sell products.', user)

    def send_buyer_email(self, bid):
        content = 'You have successfully pay for the product, we will email more details'
        self.send_email('Successfull Payment', content, bid.user)

    def send_seller_email(self, bid):
        content = 'Admin successfully pay for the items.'
        self.send_email('Successful Payment', content, bid.product_to_bid_on.seller)

    def send_email_to_seller(self, bid):
        content = 'Somebody bid on your product:{}, size: {}|{}, amount: ${}'.format(bid.product_to_bid_on.title,
                                                                                   bid.shoe_size.shoe_size,
                                                                                   bid.shoe_size.country,
                                                                                   bid.bid_amount)
        self.send_email('congregation Somebody Bid', content, bid.product_to_bid_on.seller)
        self.send_email_to_all_buyers(bid)

    def send_email_to_all_buyers(self, bid):
        all_users = Bid.objects.filter(product_to_bid_on=bid.product_to_bid_on, shoe_size=bid.shoe_size,
                                       bid_amount__lt=bid.bid_amount).values_list('user__email', flat=True)
        content = 'Somebody bid Higher than you. Product:{}, size: {}|{}, amount: ${}'.format(bid.product_to_bid_on.title,
                                                                                            bid.shoe_size.shoe_size,
                                                                                            bid.shoe_size.country,
                                                                                            bid.bid_amount)
        self.send_bulk_email("Somebody bid higher", content, all_users)
