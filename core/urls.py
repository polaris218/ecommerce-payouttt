from rest_framework.routers import DefaultRouter
from django.urls import path, include
from . import views

urlpatterns = [
    path('set/master/account/', views.SetAdminAccountApi.as_view()),
    path('pending/seller/payments/', views.PendingSellerPaymentsApi.as_view()),
    path('send/seller/<int:bid_id>/payments/', views.SendSellerPaymentsApi.as_view()),
]
