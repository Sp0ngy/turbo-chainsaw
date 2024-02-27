from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from users.utils import pseudonymize_data, de_pseudonymize_data


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

# TODO: remove "last_login" field, not required anymore
class User(AbstractBaseUser, PermissionsMixin):
    keycloak_id = models.CharField(
        unique=True,
        max_length=500,
        help_text="Keycloak User ID",
    )
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    address = models.OneToOneField(
        "Address", on_delete=models.SET_NULL, null=True, blank=True
    )

    USERNAME_FIELD = 'keycloak_id'
    REQUIRED_FIELDS = []  # additional fields you may require at creation

    objects = CustomUserManager()

    def __str__(self):
        return self.keycloak_id


class Resource(models.Model):
    """
    user-associated resources with a type
    """
    class ResourceTypes(models.TextChoices):
        PATIENT_PROFILE = "patient_profile", "Patient Profile"

    user = models.ForeignKey("User", on_delete=models.CASCADE)
    keycloak_resource_id = models.CharField(max_length=300)
    type = models.CharField(max_length=30, choices=ResourceTypes.choices, help_text="Classification of the resource")

    class Meta:
        unique_together = [["user", "type"]]


class AddressQuerySet(models.QuerySet):
    def _filter_or_exclude(self, negate, *args, **kwargs):
        for field in self.model.PSEUDONYMIZE_FIELDS:
            value = kwargs.pop(field, None)
            if value is not None:
                kwargs[f'_{field}'] = pseudonymize_data(value)
        return super()._filter_or_exclude(negate, *args, **kwargs)

class AddressManager(models.Manager):
    def get_queryset(self):
        return AddressQuerySet(self.model, using=self._db)

# Stolen from https://github.com/cuttlesoft/django-pseudonymization-example/blob/properties/users/models.py
class Address(models.Model):
    """
    Stores the pseudonyms of the according data.
    """

    PSEUDONYMIZE_FIELDS = ['line']

    _line = models.CharField(
        max_length=255,
        help_text="Street name, number or P.O. Box",
        null=False,
        blank=True,
    )

    @property
    def line(self):
        return de_pseudonymize_data(self._line)

    @line.setter
    def line(self, value):
        self._line = pseudonymize_data(value)

    objects = AddressManager()

    class Meta:
        verbose_name_plural = "Addresses"