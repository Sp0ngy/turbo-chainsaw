from django.db import models
from users.models import User

class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    identifier = models.CharField(
        unique=True,
        max_length=100,
        help_text="Patient Identifier",
    )
    PMI = models.OneToOneField("PersonalMedicalInformation", on_delete=models.PROTECT, null=True, blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.identifier:
            self.identifier = "P" + str(self.id)
            self.save()

    def __str__(self):
        return self.identifier

class PersonalMedicalInformation(models.Model):
    """Information, which can not be linked to a patient's identity without a connection to un-pseudonymized PII"""
    weight = models.DecimalField(
        max_digits=4, decimal_places=1, help_text="Your Weight in kg", null=False
    )
    height = models.DecimalField(
        max_digits=4, decimal_places=1, help_text="Your Height in cm", null=False
    )


