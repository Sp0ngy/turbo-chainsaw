from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

class CustomUserManager(BaseUserManager):
    def create_user(self, keycloak_id, password=None, **extra_fields):
        if not keycloak_id:
            raise ValueError('The Keycloak ID must be set')
        user = self.model(keycloak_id=keycloak_id, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, keycloak_id, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(keycloak_id, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    keycloak_id = models.CharField(
        unique=True,
        max_length=500,
        help_text="Keycloak User ID",
    )
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)

    USERNAME_FIELD = 'keycloak_id'
    REQUIRED_FIELDS = []  # additional fields you may require at creation

    objects = CustomUserManager()

    def __str__(self):
        return self.keycloak_id

