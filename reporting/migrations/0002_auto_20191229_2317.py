# Generated by Django 2.1.4 on 2019-12-29 16:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reporting', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='reportinghistory',
            name='user_assignee_display',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
        migrations.AddField(
            model_name='reportinghistory',
            name='user_assignee_id',
            field=models.CharField(blank=True, max_length=250, null=True),
        ),
    ]