# Generated by Django 4.2.7 on 2023-11-29 21:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0008_roomtype_max_adults_roomtype_min_adults'),
    ]

    operations = [
        migrations.RenameField(
            model_name='roomtype',
            old_name='min_adults',
            new_name='max_kids',
        ),
    ]
