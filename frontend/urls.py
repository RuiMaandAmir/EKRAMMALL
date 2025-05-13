from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'banners', views.BannerViewSet)
router.register(r'navigations', views.NavigationViewSet)
router.register(r'layouts', views.HomeLayoutViewSet)
router.register(r'special-pages', views.SpecialPageViewSet)

urlpatterns = [
    path('', include(router.urls)),
] 