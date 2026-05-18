from rest_framework import generics, permissions, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from .models import CustomUser, UserRole
from .serializers import (
    UserSerializer, AdminCreateUserSerializer,
    UserOptionSerializer, AdminUserSerializer, ChangePasswordSerializer
)
from .permissions import IsAdmin, IsAdminOrProjectOwner
from rest_framework_simplejwt.views import TokenObtainPairView
from django.conf import settings
from axes.models import AccessAttempt
from axes.utils import reset



class AdminCreateUserView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    permission_classes = (IsAdmin,)
    serializer_class = AdminCreateUserSerializer

class UserDetailView(generics.RetrieveUpdateAPIView):
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
    queryset = CustomUser.objects.filter(is_active=True, role=UserRole.USER).order_by('first_name')


class AllUsersListView(generics.ListAPIView):
    """
    GET /api/users/all/
    Returns ALL active users (all roles) for room member selection.
    Accessible by Admin and Project Owner.
    """
    serializer_class = UserOptionSerializer
    permission_classes = [IsAdminOrProjectOwner]
    queryset = CustomUser.objects.filter(is_active=True).order_by('first_name')


class AdminUserListView(generics.ListCreateAPIView):
    """
    GET  /api/users/admin/  — List ALL users (all roles, active and inactive).
    POST /api/users/admin/  — Create a new user with role selection.
    Admin only.
    """
    serializer_class = AdminUserSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        return CustomUser.objects.all().order_by('first_name')

    def get_serializer_class(self):
        # Use full create serializer for POST (needs password field)
        if self.request.method == 'POST':
            return AdminCreateUserSerializer
        return AdminUserSerializer


class AdminUserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/users/admin/<id>/  — Retrieve a single user.
    PATCH  /api/users/admin/<id>/  — Update role, name, or is_active.
    DELETE /api/users/admin/<id>/  — Soft deactivate (is_active = False).
    Admin only. Admins cannot modify or deactivate their own account.
    """
    serializer_class = AdminUserSerializer
    permission_classes = [IsAdmin]
    queryset = CustomUser.objects.all()

    def _guard_self_modification(self, request, obj):
        """Prevent admin from modifying their own account."""
        if obj.id == request.user.id:
            raise PermissionDenied("You cannot modify your own account from the Admin Panel.")

    def update(self, request, *args, **kwargs):
        obj = self.get_object()
        self._guard_self_modification(request, obj)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        obj = self.get_object()
        self._guard_self_modification(request, obj)
        # Soft delete: deactivate instead of removing from the database
        obj.is_active = False
        obj.save()
        return Response(
            {"detail": f"User '{obj.email}' has been deactivated."},
            status=status.HTTP_200_OK
        )

class ChangePasswordView(generics.GenericAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        if not user.check_password(serializer.validated_data.get('old_password')):
            return Response({"detail": "Incorrect current password."}, status=status.HTTP_400_BAD_REQUEST)
        
        user.set_password(serializer.validated_data.get('new_password'))
        user.save()
        return Response({"detail": "Password updated successfully."}, status=status.HTTP_200_OK)

class CustomTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        return response

    def handle_exception(self, exc):
        response = super().handle_exception(exc)
        
        if response.status_code == 401:
            # Calculate attempts left
            username = self.request.data.get('email')
            if username:
                attempts = AccessAttempt.objects.filter(username=username).first()
                failure_limit = getattr(settings, 'AXES_FAILURE_LIMIT', 5)
                
                # axes already increments the failure count before we reach this handler
                current_failures = attempts.failures_since_start if attempts else 1
                attempts_left = max(0, failure_limit - current_failures)
                
                response.data['attempts_left'] = attempts_left
                if attempts_left > 0:
                    unit = "attempt" if attempts_left == 1 else "attempts"
                    response.data['detail'] = f"Invalid credentials. {attempts_left} {unit} left before lockout."
                else:
                    response.status_code = status.HTTP_429_TOO_MANY_REQUESTS
                    response.data['lockout_duration'] = int(settings.AXES_COOLOFF_TIME.total_seconds())
                    response.data['detail'] = f"Invalid credentials. Your account is now locked for {response.data['lockout_duration']} seconds."
        
        return response
