from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'orders', views.OrderViewSet, basename='order')
router.register(r'payments', views.PaymentViewSet, basename='payment')
router.register(r'refunds', views.RefundViewSet)

urlpatterns = [
    path('cart/apply-distributor-code/', views.ApplyDistributorCodeView.as_view(), name='apply-distributor-code'),
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('orders/<str:order_number>/pay/', views.CreatePaymentView.as_view(), name='create-payment'),
    path('orders/<str:order_number>/refund/', views.CreateRefundView.as_view(), name='create-refund'),
    path('payment/callback/', views.PaymentCallbackView.as_view(), name='payment-callback'),
    path('alipay/callback/', views.AlipayCallbackView.as_view(), name='alipay-callback'),
]

urlpatterns += router.urls 