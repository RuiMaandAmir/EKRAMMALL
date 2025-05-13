from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import GenerateDistributionLinkView

router = DefaultRouter()
router.register(r'categories', views.CategoryViewSet)
router.register(r'products', views.ProductViewSet)
router.register(r'products/(?P<product_pk>\d+)/images', views.ProductImageViewSet, basename='product-image')
router.register(r'products/(?P<product_pk>\d+)/specifications', views.ProductSpecificationViewSet, basename='product-specification')
router.register(r'reviews', views.ProductReviewViewSet, basename='review')
router.register(r'replies', views.ReviewReplyViewSet, basename='reply')

app_name = 'products'

urlpatterns = [
    path('', include(router.urls)),
    path('category-tree/', views.CategoryTreeView.as_view(), name='category-tree'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('product/<int:product_id>/generate-distribution-link/', GenerateDistributionLinkView.as_view(), name='generate_distribution_link'),
] 