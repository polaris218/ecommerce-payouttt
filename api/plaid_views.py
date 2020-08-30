from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.PLAID_payments import PalidPayments
from api.serializers import PlaidSerializer


class ExchangePlaidTokenView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        plaid_payment, serializer_data = PalidPayments().exchange_token(self.request.user,
                                                                        request.data.get('public_token', None),
                                                                        request.data.get('account_id', None))
        if plaid_payment:
            serializer_data = PlaidSerializer(plaid_payment, many=False).data
            return Response(serializer_data, status=status.HTTP_200_OK)
        return Response(serializer_data, status=status.HTTP_400_BAD_REQUEST)
