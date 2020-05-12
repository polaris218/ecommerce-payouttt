from rest_framework.routers import DefaultRouter
from django.urls import path, include
from . import views

router = DefaultRouter()

router.register('create-bid', views.CreateBidViewset, basename="createBid")
router.register('verified-seller-application', views.SellerVerificationRequest, basename="requestSellerVerification")

router.register('create-product', views.CreateProductViewset, basename="createProduct")
router.register('verified-buyer-application', views.VerificationRequest, basename="requestVerification")

router.register('create-seller', views.CreateSellerViewset, basename="createUser")
router.register('feedback', views.FeedbackViewset, basename="feedback")

urlpatterns = [
    path('', include(router.urls)),
    path('product-search-query/', views.ListProducts.as_view()),
    # path('bid-search-query/', views.ListBids.as_view()),
    path('featured/', views.ListFeaturedProducts.as_view()),
    path('set/master/account/', views.ListFeaturedProducts.as_view()),
    path("list-products/", views.ListProducts.as_view()),
    path("list-shoes/", views.ListAllShoeSizes.as_view()),
    path("list-bids/", views.ListBidsView.as_view()),
    path("pay/<int:id>/bid/", views.PayBidView.as_view()),
    path("bid/<int:id>/stripe/key/", views.StripeBidPaymentKey.as_view()),
    path("history/", views.HistoryBidsView.as_view()),
    path("seller/history/", views.SellerHistoryBidsView.as_view()),
    path("stripe/payment/key/", views.StripePaymentKeyView.as_view()),
    path("stripe/add/payment/method/", views.AddStripePaymentMethodView.as_view()),
]
