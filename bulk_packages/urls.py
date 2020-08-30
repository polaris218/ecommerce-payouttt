from rest_framework.routers import DefaultRouter
from django.urls import path, include
from . import views

router = DefaultRouter()

router.register('operations', views.PackageViewset, basename="create-package")
urlpatterns = [
    path('', include(router.urls)),
    path("list-all/", views.ListAllPackages.as_view()),
    path("<int:id>/add/product/", views.AddProductInPackage.as_view()),
]
