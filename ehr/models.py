from django.db import models

class Patient(models.Model):
    identifier = models.CharField(
        unique=True,
        max_length=100,
        help_text="Patient Identifier",
    )
    PMI = models.OneToOneField("PersonalMedicalInformation", on_delete=models.PROTECT)
    pseudonymized_PII = models.OneToOneField("PseudonymizedPersonalIdentifyableInformation", on_delete=models.PROTECT)

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


class PseudonymizedPersonalIdentifyableInformation(models.Model):
    """Information, which identifies a user if not pseudonymized"""
    first_name = models.CharField(max_length=100, help_text="First Name")
    last_name = models.CharField(max_length=100, help_text="Last Name")


