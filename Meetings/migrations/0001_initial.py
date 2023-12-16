# Generated by Django 4.2.5 on 2023-12-15 18:00

import Meetings.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Meeting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('UID', models.TextField(default=Meetings.models.generate_UID)),
                ('type', models.CharField(choices=[('public', 'Public Meeting'), ('conference', 'Conference Meeting'), ('asktojoin', 'Ask To Join Meeting'), ('onetoone', 'One To One Meeting')], max_length=15)),
                ('allowed_participants', models.ManyToManyField(related_name='allowed_meetings', to=settings.AUTH_USER_MODEL)),
                ('blacklisted_participants', models.ManyToManyField(related_name='blacklisted_meetings', to=settings.AUTH_USER_MODEL)),
                ('host', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='hosted_meetings', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]