from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import CustomUser, UserRole

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'first_name', 'last_name', 'role', 'date_joined', 'is_staff', 'is_superuser')
        read_only_fields = ('date_joined',)

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = CustomUser
        fields = ('email', 'password', 'first_name', 'last_name')

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            role=UserRole.USER  # Always default to user for public registration
        )
        return user

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
