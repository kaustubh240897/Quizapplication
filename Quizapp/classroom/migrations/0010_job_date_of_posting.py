# Generated by Django 2.1.2 on 2018-11-01 09:44

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('classroom', '0009_auto_20181101_0227'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='date_of_posting',
            field=models.DateField(default=datetime.date.today),
        ),
    ]
