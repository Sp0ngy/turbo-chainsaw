# Generated by Django 4.2.6 on 2024-02-27 10:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0008_address_user_address'),
    ]

    operations = [
        migrations.RenameField(
            model_name='address',
            old_name='city',
            new_name='_city',
        ),
        migrations.RenameField(
            model_name='address',
            old_name='country',
            new_name='_country',
        ),
        migrations.RenameField(
            model_name='address',
            old_name='line',
            new_name='_line',
        ),
        migrations.RenameField(
            model_name='address',
            old_name='postal_code',
            new_name='_postal_code',
        ),
        migrations.RenameField(
            model_name='address',
            old_name='state',
            new_name='_state',
        ),
    ]