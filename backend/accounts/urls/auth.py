from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token
from . import views

urlpatterns = [
    path('login/', obtain_auth_token, name='api_token_auth'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('refresh-token/', views.RefreshTokenView.as_view(), name='refresh_token'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
] 