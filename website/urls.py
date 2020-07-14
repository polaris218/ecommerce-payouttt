# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from website import views
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.IndexView.as_view(), name='web-home'),
    path('category-details/', views.CategoryDetailsView.as_view(), name='web-category-detail'),
    path('selling/', views.SellingView.as_view(), name='selling'),
    path('app/', views.AppView.as_view(), name='web_app'),
    path('news/', views.NewsView.as_view(), name='web_news'),
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
]
