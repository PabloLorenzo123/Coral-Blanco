# Generated by Django 4.2.7 on 2023-12-03 14:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('booking', '0009_reservationcart_adults_reservationcart_children'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reservationcart',
            name='adults',
            field=models.IntegerField(default=0, null=True),
        ),
        migrations.AlterField(
            model_name='reservationcart',
            name='children',
            field=models.IntegerField(default=0, null=True),
        ),
    ]
