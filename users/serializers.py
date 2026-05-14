from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser, UserRole

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'first_name', 'last_name', 'role', 'date_joined', 'is_staff', 'is_superuser')
        read_only_fields = ('date_joined',)



class AdminCreateUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = CustomUser
        fields = ('email', 'password', 'first_name', 'last_name', 'role', 'is_staff', 'is_superuser')

    def create(self, validated_data):
        # Determine if we should create a staff/superuser based on fields
        role = validated_data.get('role', UserRole.USER)
        is_staff = validated_data.get('is_staff', False)
        is_superuser = validated_data.get('is_superuser', False)

        # If role is admin, force staff
        if role == UserRole.ADMIN:
            is_staff = True

        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            role=role,
            is_staff=is_staff,
            is_superuser=is_superuser
        )
        return user


class UserOptionSerializer(serializers.ModelSerializer):
    """Minimal serializer for task assignment dropdowns."""
    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'first_name', 'last_name', 'role')


class AdminUserSerializer(serializers.ModelSerializer):
    """Full serializer for Admin Panel user management."""
    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'first_name', 'last_name', 'role', 'is_active', 'date_joined')
        read_only_fields = ('id', 'email', 'date_joined')

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    confirm_password = serializers.CharField(required=True)

    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "Passwords do not match."})
        return attrs
