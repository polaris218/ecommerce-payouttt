from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.Dwolla_payment_management import DwollaPayment
from accounts.models import User, FundingSource
from accounts.serializers import UserSerializer, UserUpdateSerializer, IAVTokenSerializer, FundingSourceSerializer, \
    PersonalAccount
from core import EmailHelper
from core.views import BaseView


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
                try:
                    payment.create_customer(user)
                    EmailHelper.Email().send_welcome_email(user)
                except:
                    pass
                return Response({"message": "User Created Successfully"}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(BaseView):
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
