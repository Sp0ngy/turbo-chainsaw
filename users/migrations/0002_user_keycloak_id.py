# Generated by Django 4.2.6 on 2024-02-19 12:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='keycloak_id',
            field=models.CharField(default=1, help_text='Patient Identifier', max_length=500, unique=True),
            preserve_default=False,
        ),
    ]
