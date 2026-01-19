from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models

from .managers import CustomUserManager


class CustomUser(AbstractBaseUser, PermissionsMixin):
    class UserType(models.IntegerChoices):
        SUPERADMIN = 1, "SuperAdmin"
        USER = 2, "User"

    name = models.CharField(max_length=150)
    user_type = models.PositiveSmallIntegerField(
        choices=UserType.choices, default=UserType.USER
    )
    email = models.EmailField(
        unique=True,
        error_messages={
            "unique": "A user with this email already exists.",
            "invalid": "Enter a valid email address.",
        },
    )
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]

    def __str__(self):
        return f"{self.name} ({self.get_user_type_display()})"


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Post(BaseModel):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="posts")
    content = models.TextField(blank=True)
    image = models.ImageField(upload_to="posts/images/", null=True, blank=True)
    likes = models.ManyToManyField(CustomUser, related_name="liked_posts", blank=True)

    def __str__(self):
        return f"Post {self.id} by {self.user.email}"
