from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    RegisterView, UserDetailView, AdminCreateUserView,
    UserListView, AllUsersListView, AdminUserListView, AdminUserDetailView,
    CustomTokenObtainPairView, ChangePasswordView
)

from axes.decorators import axes_dispatch

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', axes_dispatch(CustomTokenObtainPairView.as_view()), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('user-profile/', UserDetailView.as_view(), name='user_profile'),
    path('list/', UserListView.as_view(), name='user_list'),
    path('all/', AllUsersListView.as_view(), name='all_users'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    # Admin panel endpoints
    path('admin/create-user/', AdminCreateUserView.as_view(), name='admin_create_user'),
    path('admin/', AdminUserListView.as_view(), name='admin_user_list'),
    path('admin/<int:pk>/', AdminUserDetailView.as_view(), name='admin_user_detail'),
]
