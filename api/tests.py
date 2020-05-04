from django.test import TestCase
from .models import VerifiedUserApplication

# Create your tests here.
class VerificationTestCase(TestCase):
    def setUp(self):
        VerifiedUserApplication.objects.create(payouttt_username="test_user", email_address="test@payouttt.com")
        VerifiedUserApplication.objects.create(payouttt_username="bravo_user", email_address="admin@payouttt.com")

    def test_verification_request(self):
        test_alpha = VerifiedUserApplication.objects.get(payouttt_username="test_user")
        test_bravo = VerifiedUserApplication.objects.get(payouttt_username="bravo_user")

        test_romeo = VerifiedUserApplication.objects.get(email_address="test@payouttt.com")
        test_tango = VerifiedUserApplication.objects.get(email_address="admin@payouttt.com")
