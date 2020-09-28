# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from dashboard import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    # Matches any html file - to be used for gentella
    # Avoid using your .html in your resources.
    # Or create a separate django app.
    re_path(r'^.*\.html', views.pages, name='pages'),

    # The home page
    path('', views.IndexView.as_view(), name='home'),
    path('dashboard/address/', views.AddressView.as_view(), name='address'),
    path('suggestions/', views.ProductSuggestionsView.as_view(), name='product_suggestions'),
    path('feedbacks/', views.DashboardFeedback.as_view(), name='dashboard-feedback'),
    path('dashboard/typo/', views.TypoView.as_view(), name='typo'),
    path('dashboard/paid/orders/', views.NonPaidOrdersView.as_view(), name='non_paid_orders'),
    path('dashboard/all_orders/', views.AllOrdersView.as_view(), name='all_orders'),
    path('dashboard/all_paid_orders/', views.AllPaidOrdersView.as_view(), name='all_paid_orders'),
    path('dashboard/transfer_fund/', views.TransferFundsView.as_view(), name='transfer_fund'),
    path('dashboard/remove/order/<int:id>/', views.OrderDeleteView.as_view(), name='remove-order'),
    path('login/', views.login_view, name="login"),
    path('register/', views.register_user, name="register"),
    path("logout/", LogoutView.as_view(), name="logout")
]
