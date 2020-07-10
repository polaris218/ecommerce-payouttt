from rest_framework import generics, permissions, viewsets, filters, status
from rest_framework.response import Response
from rest_framework.views import APIView

from addresses.address_validation import ShippoAddressManagement
from api.models import Product
from bulk_packages import models
from bulk_packages import serializers


class ListAllPackages(generics.ListAPIView):
    queryset = models.Package.objects.filter(sold=False)
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


class AddProductInPackage(APIView):
    queryset = models.Package.objects.filter(sold=False)
    serializer_class = serializers.PackageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return models.Package.objects.filter(id=self.kwargs.get('id'), seller=self.request.user, sold=False).first()

    def get_product(self, post_data):
        return Product.objects.filter(id=post_data.get('product_id')).first()

    def post(self, request, *args, **kwargs):
        package = self.get_object()
        error = ''
        if package:
            product = self.get_product(request.data)
            if product:
                if product not in package.products.all():
                    package.products.add(product)
                else:
                    error = 'This product is already in package.'
            else:
                error = 'This product does not exist.'

            if not error:
                return Response(serializers.PackageSerializer(instance=package, many=False).data,
                                status=status.HTTP_200_OK)
        else:
            error = "Package does not exist"
        return Response({"error": error}, status=status.HTTP_400_BAD_REQUEST)
