from rest_framework import generics, permissions
from .models import CustomUser
from .serializers import RegisterSerializer, UserSerializer, AdminCreateUserSerializer, UserOptionSerializer
from .permissions import IsAdmin, IsAdminOrProjectOwner

class RegisterView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer

class AdminCreateUserView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    permission_classes = (IsAdmin,)
    serializer_class = AdminCreateUserSerializer

class UserDetailView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user


class UserListView(generics.ListAPIView):
    """
    GET /api/users/list/
    Returns minimal user info for assignment dropdowns.
    Only accessible by Admin and Project Owner.
    """
    serializer_class = UserOptionSerializer
    permission_classes = [IsAdminOrProjectOwner]
    queryset = CustomUser.objects.filter(is_active=True).order_by('first_name')
