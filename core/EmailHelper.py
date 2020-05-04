from django.core.mail import send_mail
from django.conf import settings


class Email(object):

    def send_email(self, subject, content, user):
        send_mail(subject, content, settings.EMAIL_HOST_USER, [user.email], fail_silently=False, )

    def send_welcome_email(self, user):
        self.send_email('Welcome to Payouttt', 'Welcome to Payouttt, you can now buy and sell products.', user)

    def send_buyer_email(self, bid):
        content = 'You have successfully pay for the product, we will email more details'
        self.send_email('Successfull Payment', content, bid.user)

    def send_seller_email(self, bid):
        content = 'Admin successfully pay for the items.'
        self.send_email('Successful Payment', content, bid.product_to_bid_on.seller)
