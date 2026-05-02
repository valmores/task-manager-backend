from rest_framework import generics, permissions
from .models import CustomUser
from .serializers import RegisterSerializer, UserSerializer, AdminCreateUserSerializer
from .permissions import IsAdmin

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
