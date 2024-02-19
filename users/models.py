from django.db import models
from django.contrib.auth.models import AbstractUser

# TODO: get rid of the fields username, password, as they are not required anymore, only keep fields which store pseudonymized-PII and status fields
class User(AbstractUser):
    keycloak_id = models.CharField(
        unique=True,
        max_length=500,
        help_text="Keycloak User ID",
        null=True,
        blank=True
    )

