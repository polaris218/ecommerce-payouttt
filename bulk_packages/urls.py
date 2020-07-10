from rest_framework.routers import DefaultRouter
from django.urls import path
from . import views

router = DefaultRouter()

router.register('operations', views.PackageViewset, basename="create-package")
urlpatterns = [
    path("list-all/", views.ListAllPackages.as_view()),
]
