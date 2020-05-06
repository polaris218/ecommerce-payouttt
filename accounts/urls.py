from django.urls import path
from rest_framework_simplejwt import views as jwt_views
from accounts import views

urlpatterns = [
    path('api/user/create/', views.UserCreate.as_view(), name='account-create'),
    path('api/user/change/password/', views.ChangePasswordView.as_view(), name='change-password'),
    path('api/user/profile/', views.UserProfileView.as_view(), name='account-profile'),
    path('api/token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
    path('api/generate/iav_token/', views.GenerateIAVTokenView.as_view(), name='generate_iav_token'),
    path('api/add/funding/source/', views.FundingSourceView.as_view(), name='add_funding_source'),
    path('api/verified/buyer/account/', views.VerifiedBuyerAccountView.as_view(), name='add_verified_account'),

    # Test urls
    path('add/account/', views.AddAccountView.as_view(), name='add_account'),
    path('pay/stripe/', views.StripePaymentView.as_view(), name='stripe'),
    path('charge/', views.charge, name='charge'),
]
