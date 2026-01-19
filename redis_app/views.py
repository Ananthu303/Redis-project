from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import CustomUser, Post
from .serializers import (
    LoginSerializer,
    RegisterSerializer,
    TokenRefreshSerializer,
    TokenSerializer,
    UserDetailSerializer,
    PostSerializer,
)
from .services import Utils
from .mixins import IsOwnerMixin
from django.core.cache import cache


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.action == "register":
            return RegisterSerializer
        if self.action in ["update", "partial_update", "me"]:
            return UserDetailSerializer
        if self.action == "login":
            return LoginSerializer
        if self.action == "refresh_token":
            return TokenRefreshSerializer
        return RegisterSerializer

    @action(detail=False, methods=["post"], url_path="register")
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        response_serializer = UserDetailSerializer(user)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"], url_path="login")
    def login(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token_pair = Utils.generate_token_pair(user)
        token_serializer = TokenSerializer(token_pair)
        return Response(token_serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def me(self, request):
        user = request.user
        cache_key = Utils.user_me_cache_key(user.id)
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data, status=status.HTTP_200_OK)
        serializer = UserDetailSerializer(user)
        cache.set(cache_key, serializer.data, timeout=60 * 5)  # 5 min
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="token/refresh")
    def refresh_token(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(
            {"access": serializer.validated_data["access"]},
            status=status.HTTP_200_OK,
        )


class PostViewSet(IsOwnerMixin, viewsets.ModelViewSet):
    queryset = (
        Post.objects.select_related("user")
        .prefetch_related("likes")
        .order_by("-created_at")
    )
    serializer_class = PostSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            return [AllowAny()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(user_id=self.request.user.id)

    @action(detail=True, methods=["post"])
    def like(self, request, pk=None):
        post = self.get_object()
        user_id = request.user.id
        if post.likes.filter(id=user_id).exists():
            post.likes.remove(user_id)
        else:
            post.likes.add(user_id)
        serializer = self.get_serializer(post)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=["get"])
    def me(self, request):
        posts = self.queryset.filter(user_id=request.user.id)
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
