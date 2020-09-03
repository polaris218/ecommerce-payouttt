# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path, include
from django.views.decorators.csrf import csrf_exempt

from profiles import views
from django.contrib.auth.views import LogoutView
from two_factor.urls import urlpatterns as tf_urls

urlpatterns = [
    path('2f/', include(tf_urls)),
    path('', views.ProfileView.as_view(), name='web-profile'),
    path('security/', views.SecurityView.as_view(), name='web-security'),
    path('selling/', views.SellingView.as_view(), name='web-selling'),
    path('web-buying/', views.BuyingView.as_view(), name='web-admin-buying'),
    path('web-orders/', views.OrdersView.as_view(), name='web-orders'),
    path('wen-dashboard/', views.DashboardView.as_view(), name='web-dashboard'),
    path('web-setting/', views.SettingsView.as_view(), name='web-setting'),
    path('password-reset/', views.PasswordResetView.as_view(), name='password-reset'),
    path('change-user-name/', csrf_exempt(views.ChangeUserName.as_view()), name='change-user-name'),
    path('change-return-address/', csrf_exempt(views.ChangeReturnAddress.as_view()), name='change-return-address'),
    path('user_address/', csrf_exempt(views.UserAddressView.as_view()), name='user_address_update'),
    path('payment_method_added_success/', csrf_exempt(views.PaymentMethodAddSuccess.as_view()),
         name='payment_method_added_success'),
    path('feedback/', csrf_exempt(views.FeedBack.as_view()), name='feedback'),
    path('bid_pay_success_web', views.BidPaySuccessWeb.as_view(), name='PayForBidViewSuccess'),
    path('bid_pay_fail_web', views.BidPayFailWeb.as_view(), name='PayForBidViewFailed'),
    path('PayForBidWebView/<int:bid_id>/', csrf_exempt(views.PayForBidWebView.as_view()), name='PayForBidWebView'),
]
