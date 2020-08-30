from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.Dwolla_payment_management import DwollaPayment
from accounts.models import User
from accounts.serializers import UserUpdateSerializer, UserProfileSerializer
from api.models import BidPayment, Bid
from api.serializers import BidSerializer


class BaseView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserUpdateSerializer
    model_class = User

    def post(self, request):
        serializer = self.serializer_class(self.request.user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        instances = self.model_class.objects.filter(user=self.request.user)
        serializer = self.serializer_class(instances, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SetAdminAccountApi(APIView):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    serializer_class = UserProfileSerializer
    model_class = User

    def post(self, request):
        DwollaPayment().set_master_account(self.request.user)
        serializer = self.serializer_class(self.request.user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PendingSellerPaymentsApi(APIView):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    serializer_class = BidSerializer
    model_class = Bid

    def get_non_paid_bids(self):
        bid_ids = list(BidPayment.objects.filter(bid__paid=True, seller_url__isnull=True).values_list('bid', flat=True))
        return Bid.objects.filter(id__in=bid_ids)

    def get(self, request):
        serializer = self.serializer_class(self.get_non_paid_bids(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SendSellerPaymentsApi(APIView):
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    serializer_class = BidSerializer
    model_class = Bid

    def get_bid_payment(self, bid_id):
        return BidPayment.objects.filter(bid__paid=True, seller_url__isnull=True, bid_id=bid_id).first()

    def post(self, request, *args, **kwargs):
        bid_id = kwargs.get('bid_id')
        bid_payment = self.get_bid_payment(bid_id)
        DwollaPayment().send_seller_payment(bid_payment)
        serializer = self.serializer_class(bid_payment.bid, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
