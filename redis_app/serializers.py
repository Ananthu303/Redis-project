from rest_framework import serializers
from rest_framework.exceptions import NotAuthenticated, ValidationError
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from .models import CustomUser, Post


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ("id", "name", "email", "user_type")


class RegisterSerializer(serializers.ModelSerializer):
    password_1 = serializers.CharField(write_only=True)
    password_2 = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ["name", "email", "user_type", "password_1", "password_2"]

    def validate(self, value):
        if value["password_1"] != value["password_2"]:
            raise ValidationError("Passwords do not match.")
        return value

    def create(self, validated_data):
        password = validated_data.pop("password_1")
        validated_data.pop("password_2")
        user = CustomUser.objects.create_user(password=password, **validated_data)
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            raise ValidationError("No user found with this email")

        if not user.check_password(password):
            raise ValidationError("Wrong password.")

        data["user"] = user
        return data


class TokenSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()


class TokenRefreshSerializer(serializers.Serializer):
    refresh = serializers.CharField()

    def validate(self, data):
        refresh_token = data.get("refresh")
        try:
            refresh = RefreshToken(refresh_token)
            return {"access": str(refresh.access_token)}
        except TokenError:
            raise NotAuthenticated("Invalid or expired refresh token.")


class PostSerializer(serializers.ModelSerializer):
    content = serializers.CharField(required=True)
    user = UserDetailSerializer(read_only=True)
    total_likes = serializers.IntegerField(source="likes.count", read_only=True)

    class Meta:
        model = Post
        fields = [
            "id",
            "user",
            "content",
            "image",
            "total_likes",
            "created_at",
        ]
        read_only_fields = ["user", "total_likes", "created_at"]
