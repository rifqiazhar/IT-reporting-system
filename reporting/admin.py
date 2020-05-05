from django.contrib import admin

# Register your models here.
from reporting.models import ReportingHistory, FeatureSetting

# Text to put at the end of each page's <title>.
admin.site.site_title = ('IT Support Reporting System site')

# Text to put in each page's <h1> (and above login form).
admin.site.site_header = ('IT Support Reporting System Admin')


class ReportingHistoryAdmin(admin.ModelAdmin):
    def __init__(self, *args, **kwargs):
        super(ReportingHistoryAdmin, self).__init__(*args, **kwargs)
        self.list_display_links = None

    def has_add_permission(self, request, obj=None):
        return False

    search_fields = ['requester_user_name', 'channel_name', 'jira_card_id']
    list_display = ('cdate', 'jira_card_id', 'jira_status', 'channel_name', 'requester_user_name', 'message')


admin.site.register(ReportingHistory, ReportingHistoryAdmin)
admin.site.register(FeatureSetting)