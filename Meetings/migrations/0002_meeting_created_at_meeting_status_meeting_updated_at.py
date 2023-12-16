# Generated by Django 4.2.5 on 2023-12-15 21:13

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Meetings', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='meeting',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='meeting',
            name='status',
            field=models.CharField(choices=[('active', 'Active'), ('ended', 'Ended'), ('upcoming', 'Upcoming')], default=datetime.datetime(2023, 12, 15, 21, 13, 5, 924916, tzinfo=datetime.timezone.utc), max_length=15),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='meeting',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
    ]