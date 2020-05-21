from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.parsers import FileUploadParser, MultiPartParser
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import viewsets, permissions
from rest_framework import status
from django.http import JsonResponse
from rest_framework import filters
from rest_framework import generics
from rest_framework.response import Response

from accounts.STRIPE_payments import StripePayment
from . import serializers
from . import models

from accounts.Dwolla_payment_management import DwollaPayment
from .models import Bid
import shippo
from django.conf import settings
from api.models import ShoeSize

shippo.config.api_key = "shippo_test_48803b138ac2f2cb91e20d674886102386a45920"
shippo.config.api_version = "2018-02-08"
shippo.config.verify_ssl_certs = True
shippo.config.rates_req_timeout = 30.0


class SellerVerificationRequest(viewsets.ModelViewSet):
    serializer_class = serializers.VerifySerializer
    queryset = models.VerifiedSellerApplication.objects.all()

    def perform_create(self, serializer):
        if serializer.is_valid():
            serializer.save()


class VerificationRequest(viewsets.ModelViewSet):
    serializer_class = serializers.VerifySerializer
    queryset = models.VerifiedUserApplication.objects.all()

    def perform_create(self, serializer):
        if serializer.is_valid():
            serializer.save()


class CreateProductViewset(viewsets.ModelViewSet):
    serializer_class = serializers.ProductSerializer
    queryset = models.Product.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    filter_backends = (filters.SearchFilter,)
    search_fields = ('title', 'brand',)

    def get_queryset(self):
        return self.queryset.filter(seller=self.request.user)

    def create(self, request, *args, **kwargs):
        request_data = request.data.copy()
        request_data['seller'] = self.request.user.pk
        serializer = self.get_serializer(data=request_data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        if serializer.is_valid():
            product = serializer.save()
            shoe_sizes = ShoeSize.objects.filter(id__in=self.request.data.get('shoe_sizes', '').split(','))
            for shoe in shoe_sizes:
                if shoe not in product.shoe_sizes.all():
                    product.shoe_sizes.add(shoe)


class CreateSellerViewset(viewsets.ModelViewSet):
    serializer_class = serializers.SellerSerializer
    queryset = models.Seller.objects.all()

    def perform_create(self, serializer):
        if serializer.is_valid():
            serializer.save()


class ListProducts(generics.ListAPIView):
    queryset = models.Product.objects.all().order_by('-id')
    serializer_class = serializers.ProductSerializer
    permission_classes = []
    filter_backends = [DjangoFilterBackend, SearchFilter, filters.OrderingFilter]
    filterset_fields = ['title', 'sku_number', 'brand', 'listing_price', 'url', 'sold', 'shoe_sizes']
    search_fields = ['title', 'sku_number', 'brand']
    ordering_fields = ['listing_price', ]


class ListAllShoeSizes(generics.ListAPIView):
    queryset = models.ShoeSize.objects.all()
    serializer_class = serializers.ShoeSizeSerializer
    permission_classes = [permissions.IsAuthenticated]


class ListBidsView(generics.ListAPIView):
    queryset = models.Bid.objects.all()
    serializer_class = serializers.BidSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = (filters.SearchFilter,)
    search_fields = ('product_to_bid_on__title', 'shoe_size__shoe_size', 'bid_amount', 'verified_account',)

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


class StripeBidPaymentKey(APIView):
    serializer_class = serializers.BidSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return Bid.objects.filter(id=self.kwargs.get('id'), user=self.request.user, paid=False).first()

    def get(self, request, *args, **kwargs):
        bid_id = kwargs.get('id')
        bid = self.get_object()
        if bid:
            if bid.can_pay():
                return Response({"key": settings.STRIPE_PUBLISHABLE_KEY}, status=status.HTTP_200_OK)
            else:
                error = "You can't pay for this bid as you bid amount is less then total amount"
        else:
            error = "No bid found"
        return Response({"error": error}, status=status.HTTP_200_OK)


class PayBidView(APIView):
    serializer_class = serializers.BidSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return Bid.objects.filter(id=self.kwargs.get('id'), user=self.request.user, paid=False).first()

    def get_admin_address(self):
        admin_addr = {
            "name": "Payouttt Team",
            "street1": "1262 Appalachian road",
            "street2": "",
            "city": "Ambler",
            "state": "PA",
            "zip": "19002",
            "country": "US",
            "phone": "+1 123 456 789",
        }
        return admin_addr

    def get_parcel(self):
        parcel = {
            "length": "14",
            "width": "10",
            "height": "6",
            "distance_unit": "in",
            "weight": "3",
            "mass_unit": "lb",
        }
        return parcel

    def set_user_tracking(self, user, bid_payment, seller=True):

        try:
            if seller:
                seller_addr = {
                    "name": user.full_name or 'Payoutttt',
                    "street1": user.street_address,
                    "city": user.city,
                    "state": str(user.state),
                    "zip": int(user.zip_code),
                    "country": "US",
                    "phone": str(user.phone_number),
                }

                shipment = shippo.Shipment.create(
                    address_from=seller_addr,
                    address_to=self.get_admin_address(),
                    parcels=[self.get_parcel()],
                    asynchronous=False
                )
            else:
                buyer_addr = {
                    "name": user.full_name or 'Payoutttt',
                    "street1": user.street_address,
                    "city": user.city,
                    "state": str(user.state),
                    "zip": int(user.zip_code),
                    "country": "US",
                    "phone": str(user.phone_number),
                }

                shipment = shippo.Shipment.create(
                    address_from=self.get_admin_address(),
                    address_to=buyer_addr,
                    parcels=[self.get_parcel()],
                    asynchronous=False
                )
            rate = shipment.rates[0]
            transaction = shippo.Transaction.create(
                rate=rate.object_id, asynchronous=False)
            if transaction.status == "SUCCESS":
                if seller:
                    bid_payment.seller_tracking = transaction.tracking_number
                    bid_payment.seller_purchase_label = transaction.label_url
                else:
                    bid_payment.purchase_tracking = transaction.tracking_number
                    bid_payment.purchase_label = transaction.label_url

            else:
                if seller:
                    bid_payment.seller_shippo_error = transaction.messages[0].get('text')
                else:
                    bid_payment.buyer_shippo_error = transaction.messages[0].get('text')
            bid_payment.save()
        except Exception as e:
            if seller:
                bid_payment.seller_shippo_error = str(e.http_body)
            else:
                bid_payment.buyer_shippo_error = str(e.http_body)
        bid_payment.save()

    def get_bid_payment(self, bid):
        return bid.bidpayment_set.all().first()

    def verify_payment_method(self, payment_method):
        try:
            return eval(payment_method).get('paymentMethod').get('id')
        except:
            return False

    def post(self, request, *args, **kwargs):
        error_message = ''
        bid = self.get_object()
        if bid:
            if not bid.can_pay():
                error_message = "You can't pay for this bid as your bid amount is less than the original price."
            else:
                if request.data.get('method') == 'dwolla':
                    if bid.user.get_fund_source() and bid.product_to_bid_on.seller.get_fund_source():
                        bid_payment = self.get_bid_payment(bid)
                        if not bid_payment:
                            bid_payment = DwollaPayment().send_payment(bid)

                        if bid_payment:
                            self.set_user_tracking(bid.user, bid_payment, seller=False)
                            self.set_user_tracking(bid.product_to_bid_on.seller, bid_payment, seller=True)
                            return Response(self.serializer_class(bid, many=False).data, status=status.HTTP_200_OK)
                        else:
                            bid.paid = False
                            bid.save()
                            error_message = "Payment not successful. Please try again later"
                    else:
                        error_message = "Both of you must have account linked."
                elif request.data.get('method') == 'stripe':
                    bid_payment = self.get_bid_payment(bid)
                    if request.user.stripe_customer_id and self.verify_payment_method(
                            request.user.stripe_payment_method):
                        if not bid_payment:
                            bid_payment = StripePayment().bid_payment(bid, request)

                        if bid_payment:
                            self.set_user_tracking(bid.user, bid_payment, seller=False)
                            self.set_user_tracking(bid.product_to_bid_on.seller, bid_payment, seller=True)
                            return Response(self.serializer_class(bid, many=False).data, status=status.HTTP_200_OK)
                        else:
                            bid.paid = False
                            bid.save()
                            error_message = "Payment not successful. Please try again later"
                    else:
                        error_message = "Please add stripe payment method first"
                else:
                    error_message = "Please specify 'method' of payment, <stripe>/<dwolla>"
        else:
            error_message = "No bid Found"
        return Response({"error": error_message}, status=status.HTTP_400_BAD_REQUEST)


class ListFeaturedProducts(generics.ListAPIView):
    queryset = models.FeaturedProduct.objects.all()
    serializer_class = serializers.FeaturedSerializer


class CreateBidViewset(viewsets.ModelViewSet):
    serializer_class = serializers.CreateBidSerializer
    queryset = models.Bid.objects.all()

    filter_backends = (filters.SearchFilter,)
    search_fields = ('product_to_bid_on__title', 'bid_amount', 'shoe_size__shoe_size', 'verified_account',)

    def create(self, request, *args, **kwargs):
        request_data = request.data.copy()
        request_data['user'] = self.request.user.pk
        serializer = self.get_serializer(data=request_data)
        serializer.is_valid(raise_exception=True)
        obj = self.perform_create(serializer)
        if obj:
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

        return Response({"message": "You have already bid on this product."}, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        if serializer.is_valid():
            product_to_bid_on = serializer.validated_data['product_to_bid_on']
            existing_bid = Bid.objects.filter(product_to_bid_on=product_to_bid_on, user=self.request.user).exists()
            if not existing_bid:
                return serializer.save()
            return False


class FeedbackViewset(viewsets.ModelViewSet):
    serializer_class = serializers.FeedbackSerializer
    queryset = models.Feedback.objects.all()


class HistoryBidsView(APIView):
    serializer_class = serializers.BidSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_objects(self, pending):
        bids = Bid.objects.filter(user=self.request.user).order_by('id')
        if pending:
            bids = bids.filter(paid=False)
        return bids

    def get(self, request, *args, **kwargs):
        pending = request.GET.get('pending', None)
        bids = self.get_objects(pending)
        return Response(self.serializer_class(bids, many=True).data, status=status.HTTP_200_OK)


class SellerHistoryBidsView(APIView):
    serializer_class = serializers.BidSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_objects(self, pending, product_id):
        bids = Bid.objects.filter(product_to_bid_on__seller=self.request.user).order_by('id')
        if product_id:
            bids = bids.filter(product_to_bid_on__id=product_id)
        if pending:
            bids = bids.filter(paid=False)
        return bids

    def get(self, request, *args, **kwargs):
        pending = request.GET.get('pending', None)
        product_id = request.GET.get('product_id', None)
        bids = self.get_objects(pending, product_id)
        return Response(self.serializer_class(bids, many=True).data, status=status.HTTP_200_OK)


class StripePaymentKeyView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        key = StripePayment().get_customer_secret(self.request.user)
        return Response({"key": key}, status=status.HTTP_200_OK)


class AddStripePaymentMethodView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        payment_method = request.data.get('payment_method', None)
        user = self.request.user
        error = "Please create stripe customer first"
        if payment_method:
            if user.stripe_customer_id and payment_method.get('paymentMethod').get('id'):
                user.stripe_payment_method = payment_method
                user.save()
                StripePayment().link_paymentmethod_with_customer(user)
                return Response({"message": "Payment Method successfully added."}, status=status.HTTP_200_OK)
        else:
            error = "Please provide payment_method"
        return Response({"message": error}, status=status.HTTP_400_BAD_REQUEST)


class BidDeleteView(APIView):
    serializer_class = serializers.BidSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return Bid.objects.filter(id=self.kwargs.get('id'), user=self.request.user, paid=False)

    def get(self, request, *args, **kwargs):
        bid = self.get_object()
        if bid:
            bid.delete()
            return Response({"message": "Bid deleted Successfully"}, status=status.HTTP_200_OK)
        else:
            error = "No bid found"
        return Response({"error": error}, status=status.HTTP_404_NOT_FOUND)


class HighLowBidsView(APIView):
    serializer_class = serializers.BidSerializer
    permission_classes = []

    def get_objects(self):
        bids = Bid.objects.filter(product_to_bid_on_id=self.kwargs.get('id'),
                                  shoe_size=self.kwargs.get('size_id')).order_by('-bid_amount')
        data = []
        if bids.first():
            data.append(bids.first())
        if bids.last() and bids.last() not in data:
            data.append(bids.last())
        return data

    def get(self, request, *args, **kwargs):
        bids = self.get_objects()
        return Response(self.serializer_class(bids, many=True).data, status=status.HTTP_200_OK)


class StripePaymentMethodView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def verify_payment_method(self, payment_method):
        try:
            payment_data = eval(payment_method).get('paymentMethod')
            card_data = payment_data.get('card')
            data = {"payment_id": payment_data.get('id'), "brand": card_data.get('brand'),
                    "country": card_data.get('country'),
                    "exp_month": card_data.get('exp_month'), "exp_year": card_data.get('exp_year'),
                    "funding": card_data.get('funding'), "last4": card_data.get('last4')}
            return data
        except:
            return False

    def get(self, request, *args, **kwargs):
        payment_method = self.verify_payment_method(self.request.user.stripe_payment_method)
        if not payment_method:
            return Response({"message": 'No Stripe Payment method Linked'}, status=status.HTTP_404_NOT_FOUND)
        return Response(payment_method, status=status.HTTP_200_OK)


class StripeDeletePaymentMethodView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def verify_payment_method(self, payment_method):
        message = "You don't have payment method integrated"
        try:
            payment_data = eval(payment_method).get('paymentMethod')
            if payment_data.get('id') == self.kwargs.get('payment_id'):
                StripePayment().detach_account(self.kwargs.get('payment_id'))
                user = self.request.user
                user.stripe_payment_method = ""
                user.save()
                message = "Successfully Detach payment method."
            else:
                message = "Invalid Payment Id."
        except:
            pass

        return message

    def post(self, request, *args, **kwargs):
        payment_method_message = self.verify_payment_method(self.request.user.stripe_payment_method)
        return Response({"message": payment_method_message}, status=status.HTTP_200_OK)
