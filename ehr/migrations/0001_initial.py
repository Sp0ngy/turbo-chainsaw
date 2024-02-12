# Generated by Django 4.2.6 on 2024-02-12 13:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='PersonalMedicalInformation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('weight', models.DecimalField(decimal_places=1, help_text='Your Weight in kg', max_digits=4)),
                ('height', models.DecimalField(decimal_places=1, help_text='Your Height in cm', max_digits=4)),
            ],
        ),
        migrations.CreateModel(
            name='PseudonymizedPersonalIdentifyableInformation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(help_text='First Name', max_length=100)),
                ('last_name', models.CharField(help_text='Last Name', max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Patient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('identifier', models.CharField(help_text='Patient Identifier', max_length=100, unique=True)),
                ('PMI', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to='ehr.personalmedicalinformation')),
                ('pseudonymized_PII', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, to='ehr.pseudonymizedpersonalidentifyableinformation')),
            ],
        ),
    ]
