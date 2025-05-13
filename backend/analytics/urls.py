from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'data-points', views.DataPointViewSet)
router.register(r'reports', views.ReportViewSet)
router.register(r'dashboards', views.DashboardViewSet)
router.register(r'alerts', views.AlertViewSet)
router.register(r'user-behaviors', views.UserBehaviorViewSet)
router.register(r'sales-analytics', views.SalesAnalyticsViewSet)
router.register(r'user-analytics', views.UserAnalyticsViewSet)
router.register(r'product-analytics', views.ProductAnalyticsViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('dashboard-summary/', views.AnalyticsViewSet.as_view({'get': 'dashboard_summary'}), name='dashboard-summary'),
    path('sales-funnel/', views.AnalyticsViewSet.as_view({'get': 'sales_funnel'}), name='sales-funnel'),
    path('user-retention/', views.AnalyticsViewSet.as_view({'get': 'user_retention'}), name='user-retention'),
    path('product-performance/', views.AnalyticsViewSet.as_view({'get': 'product_performance'}), name='product-performance'),
    path('distribution-analytics/', views.AnalyticsViewSet.as_view({'get': 'distribution_analytics'}), name='distribution-analytics'),
] 