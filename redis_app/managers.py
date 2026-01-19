from django.contrib.auth.models import BaseUserManager

class CustomUserManager(BaseUserManager):
    def create_user(self, name, password=None, **extra_fields):
        """
        Create and return a regular user with a username and password.
        """
        if not name:
            raise ValueError('The Username field must be set')
        user = self.model(name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, name, password=None, **extra_fields):
        from .models import CustomUser
        """
        Create and return a superuser with a username, password, and superadmin role.
        """
        extra_fields.setdefault('user_type', CustomUser.UserType.SUPERADMIN)
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        if not password:
            raise ValueError(_("Superuser must have a password."))

        return self.create_user(name, password, **extra_fields)
