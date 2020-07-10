from rest_framework import generics, permissions, viewsets, filters, status
from rest_framework.response import Response

from addresses.address_validation import ShippoAddressManagement
from bulk_packages import models
from bulk_packages import serializers


class ListAllPackages(generics.ListAPIView):
    queryset = models.Package.objects.first(sold=False, is_active=True)
    serializer_class = serializers.PackageSerializer
    permission_classes = [permissions.IsAuthenticated]


class PackageViewset(viewsets.ModelViewSet):
    serializer_class = serializers.PackageCreateUpdateSerializer
    queryset = models.Package.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    filter_backends = (filters.SearchFilter,)
    search_fields = ('title',)

    def get_queryset(self):
        return self.queryset.filter(seller=self.request.user)

    def create(self, request, *args, **kwargs):
        request_data = request.data.copy()
        request_data['seller'] = self.request.user.pk
        serializer = self.get_serializer(data=request_data)
        valid_address = ShippoAddressManagement().user_valid_address(self.request.user)
        if valid_address:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        return Response({"message": "Please add a valid address before listing a product."},
                        status=status.HTTP_400_BAD_REQUEST)
