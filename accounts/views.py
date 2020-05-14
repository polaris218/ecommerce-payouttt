import stripe
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render
from django.views.generic import TemplateView
from rest_framework import status, permissions
from rest_framework.generics import UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.Dwolla_payment_management import DwollaPayment
from accounts.models import User, FundingSource
from accounts.serializers import UserSerializer, UserUpdateSerializer, IAVTokenSerializer, FundingSourceSerializer, \
    PersonalAccount, ChangePasswordSerializer
from core import EmailHelper
from core.views import BaseView
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


class ChangePasswordView(UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    model = User
    permission_classes = (IsAuthenticated,)

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["Wrong password."]}, status=status.HTTP_400_BAD_REQUEST)
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            response = {
                'status': 'success',
                'code': status.HTTP_200_OK,
                'message': 'Password updated successfully',
                'data': []
            }

            return Response(response)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserCreate(APIView):
    """
    Creates the user.
    """
    serializer_class = UserSerializer

    def post(self, request, format='json'):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            if user:
                payment = DwollaPayment()
                payment.create_customer(user)
                try:
                    EmailHelper.Email().send_welcome_email(user)
                except:
                    pass
                return Response({"message": "User Created Successfully"}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(BaseView, UpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserUpdateSerializer
    model_class = User

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)

    def get_object(self):
        return self.request.user

    def post(self, request):
        serializer = self.serializer_class(self.request.user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        serializer = self.serializer_class(self.request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GenerateIAVTokenView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = IAVTokenSerializer

    def get(self, request):
        token = {'token': DwollaPayment().get_customer_iav_token(self.request.user)}
        serializer = self.serializer_class(token, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)


class FundingSourceView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FundingSourceSerializer
    model_class = FundingSource

    def post(self, request):
        request_data = request.data.copy()
        request_data['user'] = self.request.user.pk
        serializer = self.serializer_class(data=request_data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VerifiedBuyerAccountView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PersonalAccount
    model_class = FundingSource

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            DwollaPayment().create_customer(self.request.user, ssn=serializer.validated_data.get('ssn'),
                                            birth_date=serializer.validated_data.get('date_of_birth'))
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AddAccountView(TemplateView):
    template_name = 'add-account.html'


class StripePaymentView(TemplateView):
    template_name = 'stripe_payments.html'

    def get_context_data(self, **kwargs):
        kwargs.setdefault('view', self)
        kwargs['key'] = settings.STRIPE_PUBLISHABLE_KEY
        if self.extra_context is not None:
            kwargs.update(self.extra_context)
        return kwargs


def charge(request):  # new
    if request.method == 'POST':
        charge = stripe.Charge.create(
            amount=500,
            currency='usd',
            description='A Django charge',
            source=request.POST['stripeToken']
        )
        return render(request, 'charge.html')


def confirmCard(request):  # new
    # if request.method == 'POST':
    #     charge = stripe.Charge.create(
    #         amount=500,
    #         currency='usd',
    #         description='A Django charge',
    #         source=request.POST['stripeToken']
    #     )
    return render(request, 'test_stripe.html')

# charge.to_dict().get('receipt_url')
# charge.to_dict().get('amount')
