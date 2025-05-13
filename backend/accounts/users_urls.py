from django.urls import path
from .views import UserListView, UserDetailView, UserProfileViewSet, MemberLevelListView, MemberLevelDetailView

urlpatterns = [
    path('', UserListView.as_view({'get': 'list', 'post': 'create'}), name='user-list'),
    path('<int:pk>/', UserDetailView.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='user-detail'),
    path('profile/', UserProfileViewSet.as_view({'get': 'list'}), name='user-profile'),
    path('member-levels/', MemberLevelListView.as_view({'get': 'list', 'post': 'create'}), name='member-level-list'),
    path('member-levels/<int:pk>/', MemberLevelDetailView.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}), name='member-level-detail'),
] 