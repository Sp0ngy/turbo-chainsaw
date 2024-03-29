from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from users.pseudonymize_utils import mask, unmask
from users.fields import PseudonymizedField


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


class Address(models.Model):
    """
    Stores the pseudonyms of the according data.
    """
    class CountryCode(models.TextChoices):  # Acc. to ISO 3166 + TRNC
        EMPTY = "", "-----"
        DE = "DE", "Germany"
        TR = "TR", "Turkey"
        TRNC = "TRNC", "Turkish Republic of North Cyprus"
        CY = "CY", "Cyprus"
        BE = "BE", "Belgium"
        DK = "DK", "Denmark"
        FR = "FR", "France"
        LU = "LU", "Luxembourg"
        NL = "NL", "Netherlands"
        AT = "AT", "Austria"
        CZ = "CZ", "Czech Republic"
        PL = "PL", "Poland"
        CH = "CH", "Switzerland"
        LI = "LI", "Liechtenstein"

    line = PseudonymizedField(models.CharField, (mask, unmask), max_length=100, null=False, blank=True)
    country = PseudonymizedField(models.CharField, (mask, unmask), choices=CountryCode.choices, max_length=100)

    class Meta:
        verbose_name_plural = "Addresses"