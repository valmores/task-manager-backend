from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterView, UserDetailView, AdminCreateUserView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('admin/create-user/', AdminCreateUserView.as_view(), name='admin_create_user'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('user-profile/', UserDetailView.as_view(), name='user_profile'),
]
