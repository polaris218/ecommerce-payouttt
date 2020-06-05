from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from addresses.address_validation import ShippoAddressManagement
from addresses.models import Address
from addresses.serializers import AddressSerializer


class AddAddressView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AddressSerializer

    def get_object(self):
        return Address.objects.filter(user=self.request.user).first()

    def get(self, request, *args, **kwargs):
        address = self.get_object()
        return Response(self.serializer_class(instance=address, many=False).data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        request_data = request.data.copy()
        request_data['user'] = self.request.user.id
        request_data['validate'] = True
        request_data['email'] = self.request.user.email
        address = self.get_object()
        serializer = self.serializer_class(data=request_data)
        if address:
            serializer = self.serializer_class(data=request_data, instance=address)
        if serializer.is_valid():
            valid_address, message, address_id = ShippoAddressManagement().validate_address(request_data)
            if valid_address:
                address = serializer.save()
                address.is_valid = True
                address.shippo_address_id = address_id
                if self.request.user.is_staff:
                    address.admin_address = True
                address.save()
                return Response(self.serializer_class(instance=address, many=False).data, status=status.HTTP_200_OK)
            else:
                data = {"address": serializer.data, "message": message}
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
