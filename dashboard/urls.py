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
    path('dashboard/typo/', views.TypoView.as_view(), name='typo'),
    path('dashboard/paid/orders/', views.PaidOrdersView.as_view(), name='paid_orders'),
    path('login/', views.login_view, name="login"),
    path('register/', views.register_user, name="register"),
    path("logout/", LogoutView.as_view(), name="logout")
]
