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
    path('category-details/', views.CategoryDetailsView.as_view(), name='web-category-detail'),
    path('selling/', views.SellingView.as_view(), name='selling'),
    path('app/', views.AppView.as_view(), name='web_app'),
    path('news/', views.NewsView.as_view(), name='web_news'),
    # path('news/details/', views.AppView.as_view(), name='web_app'),
    path('login/', views.login_view, name="login"),
    path("logout/", LogoutView.as_view(), name="logout")
]
