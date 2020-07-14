# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from django.views.decorators.csrf import csrf_exempt

from profiles import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.ProfileView.as_view(), name='web-profile'),
    path('security/', views.SecurityView.as_view(), name='web-security'),
    path('selling/', views.SellingView.as_view(), name='web-selling'),
    path('web-buying/', views.BuyingView.as_view(), name='web-admin-buying'),
    path('wen-dashboard/', views.DashboardView.as_view(), name='web-dashboard'),
    path('web-setting/', views.SettingsView.as_view(), name='web-setting'),
    path('password-reset/', views.PasswordResetView.as_view(), name='password-reset'),
    path('change-user-name/', csrf_exempt(views.ChangeUserName.as_view()), name='change-user-name'),
    path('change-return-address/', csrf_exempt(views.ChangeReturnAddress.as_view()), name='change-return-address'),
    path('user_address/', views.UserAddressView.as_view(), name='user_address_update'),

]
