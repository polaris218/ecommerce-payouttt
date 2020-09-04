# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from django.views.decorators.csrf import csrf_exempt

from website import views
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', csrf_exempt(views.IndexView.as_view()), name='web-home'),
    path('category-details/', views.CategoryDetailsView.as_view(), name='web-category-detail'),
    path('selling/', views.SellingView.as_view(), name='selling'),
    path('app/', views.AppView.as_view(), name='web_app'),
    path('news/', views.NewsView.as_view(), name='web_news'),
    path('about/', views.AboutUsView.as_view(), name='about-us'),
    path('search/', csrf_exempt(views.SearchView.as_view()), name='web_search'),
    path('news-detail/', views.NewsDetailView.as_view(), name='web_news_detail'),
    path('product-detail/<int:product_id>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('cart/', views.WebCartView.as_view(), name='web_cart'),
    path('cart/add/<int:product_id>', csrf_exempt(views.WebCartAddView.as_view()), name='web_cart_add_product'),
    path('cart/item/delete/<int:cart_item_id>', csrf_exempt(views.WebCartItemDeleteView.as_view()),
         name='web_cart_item_delete'),
    path('product-bid/<int:product_id>/', csrf_exempt(views.WebCartBidView.as_view()), name='web_cart_bid'),
    path('product-buy/<int:product_id>/', csrf_exempt(views.WebCartBuyView.as_view()), name='web_cart_buy'),
    path('product-sell/<int:product_id>/', csrf_exempt(views.WebCartSellView.as_view()), name='web_cart_sell'),
    path('cart/checkout', views.WebCartCheckoutView.as_view(), name='web_cart_checkout'),
    path('cart/confirmation', views.WebCartConfirmationView.as_view(), name='web_cart_confirmation'),
    path('cart/thank-you', views.WebCartThankYouView.as_view(), name='web_cart_thank_you'),
    path('cart/failed-you', views.WebCartFailedView.as_view(), name='web_cart_failed'),
    path('product/suggest/', csrf_exempt(views.WebProductSuggestView.as_view()), name="product_suggest"),
    path('login/', views.login_view, name="login"),
    path('signup/', views.signup_view, name="signup"),
    path("logout/", views.logout_view, name="logout"),
    path('password-reset/', auth_views.PasswordResetView.as_view(html_email_template_name='password_reset_email.html'),
         name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'),
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='password_reset_confirm.html'), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='password_reset_complete.html'), name='password_reset_complete'),
    path('charge-stripe-payment/', views.stripe_payment_charge, name='stripe_charge'),
]
