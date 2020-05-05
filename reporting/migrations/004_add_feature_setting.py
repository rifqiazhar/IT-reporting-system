# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations

from reporting.constant import FeatureSettingName


def add_jira_feature_settings(apps, schema_editor):
    FeatureSetting = apps.get_model("reporting", "FeatureSetting")
    FeatureSetting.objects.get_or_create(is_active=True,
        feature_name=FeatureSettingName.JIRA_FEATURE_SETTING,
        category="THIRD-API",
        parameters={
            "statuses": ['to do', 'in progress', 'done', 'code review', 'qa'],
        },
        description="Feature setting for setting some API token or some setting able property for jira")

class Migration(migrations.Migration):

    dependencies = [
        ('reporting', '0003_featuresetting'),
    ]

    operations = [
        migrations.RunPython(add_jira_feature_settings,
                             migrations.RunPython.noop)
    ]
