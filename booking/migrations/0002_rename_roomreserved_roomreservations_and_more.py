# Generated by Django 4.2.7 on 2023-12-02 01:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0001_initial'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='RoomReserved',
            new_name='RoomReservations',
        ),
        migrations.RenameField(
            model_name='room',
            old_name='avaibility',
            new_name='avaliability',
        ),
    ]
