# Generated by Django 4.2.7 on 2023-12-09 16:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0002_remove_room_avaliability_remove_room_building_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='guest',
            name='card_number',
        ),
        migrations.RemoveField(
            model_name='guest',
            name='country',
        ),
        migrations.RemoveField(
            model_name='guest',
            name='csv',
        ),
        migrations.RemoveField(
            model_name='guest',
            name='expire_date',
        ),
        migrations.RemoveField(
            model_name='guest',
            name='postal_code',
        ),
        migrations.AddField(
            model_name='reservation',
            name='card_brand',
            field=models.CharField(max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='reservation',
            name='card_last4',
            field=models.CharField(max_length=4, null=True),
        ),
        migrations.AddField(
            model_name='reservation',
            name='card_payment_token',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
