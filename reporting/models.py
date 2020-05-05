from django.db import models
from django.contrib.postgres.fields import JSONField

# Create your models here.


class TimeStampedModel(models.Model):

    class Meta(object):
        abstract = True
    cdate = models.DateTimeField(auto_now_add=True)
    udate = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        #no need to worry about instance.save(update_fields=['udate'])
        #we handle that automatically
        if kwargs and kwargs.get('update_fields'):
            if 'udate' not in kwargs['update_fields']:
                kwargs['update_fields'].append("udate")
        super(TimeStampedModel, self).save(*args, **kwargs)

    def update_safely(self, **kwargs):
        """
        this method simplified update method:
        use like this:

        instance = Model.objects.get(pk=xxx)
        instance.safely_update(
          field_name1=value1,
          fiedl_name2=value2
        )
        """

        fields = []
        for kwarg in kwargs:
            setattr(self, kwarg, kwargs[kwarg])
            fields.append(kwarg)
        self.save(update_fields=fields)
        self.refresh_from_db()


class ReportingHistory(TimeStampedModel):
    id = models.AutoField(db_column='reporting_id', primary_key=True)
    requester_id = models.CharField(max_length=200)
    requester_user_name = models.CharField(max_length=200)
    message_slack_ts = models.CharField(max_length=200, blank=True, null=True)
    channel_id = models.CharField(max_length=100)
    channel_name = models.CharField(max_length=150)
    jira_card_id = models.CharField(max_length=200, blank=True, null=True)
    jira_status = models.CharField(max_length=100, blank=True, null=True)
    user_assignee_id = models.CharField(max_length=250, blank=True, null=True)
    user_assignee_display = models.CharField(max_length=250, blank=True, null=True)
    message = models.TextField()

    class Meta:
        db_table = 'reporting_history'


class FeatureSetting(TimeStampedModel):
    id = models.AutoField(db_column='feature_setting_id', primary_key=True)
    feature_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=False)
    parameters = JSONField(blank=True, null=True)
    category = models.CharField(max_length=100)
    description = models.CharField(max_length=200)

    class Meta:
        db_table = 'feature_setting'

    def __str__(self):
        return self.feature_name
