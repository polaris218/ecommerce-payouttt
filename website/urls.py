# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2019 - present AppSeed.us
"""

from django.urls import path, re_path
from website import views
from django.contrib.auth.views import LogoutView

urlpatterns = [
    path('', views.IndexView.as_view(), name='web-home'),
    path('login/', views.login_view, name="login"),
    path("logout/", LogoutView.as_view(), name="logout")
]
