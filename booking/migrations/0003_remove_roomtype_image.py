# Generated by Django 4.2.7 on 2023-11-29 19:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0002_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='roomtype',
            name='image',
        ),
    ]
