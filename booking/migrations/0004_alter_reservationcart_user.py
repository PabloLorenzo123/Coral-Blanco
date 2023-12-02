# Generated by Django 4.2.7 on 2023-12-02 01:10

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('booking', '0003_rename_roomreserved_roomreservations_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reservationcart',
            name='user',
            field=models.OneToOneField(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='cart', to=settings.AUTH_USER_MODEL),
        ),
    ]
