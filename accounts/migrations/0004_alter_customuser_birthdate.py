# Generated by Django 4.2.7 on 2023-11-28 14:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_alter_customuser_address_alter_customuser_city_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='birthdate',
            field=models.DateField(null=True),
        ),
    ]
