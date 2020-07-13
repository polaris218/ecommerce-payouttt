# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from profiles import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.ProfileView.as_view(), name='web-profile'),
    path('security/', views.SecurityView.as_view(), name='web-security'),
    path('selling/', views.SellingView.as_view(), name='web-selling'),
    path('web-buying/', views.BuyingView.as_view(), name='web-admin-buying'),
    path('wen-dashboard/', views.DashboardView.as_view(), name='web-dashboard'),
    path('web-setting/', views.SettingsView.as_view(), name='web-setting'),
]
