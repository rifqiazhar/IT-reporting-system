from django.conf.urls import url, include
from django.contrib import admin

from reporting.views import SlackEventCallbackView, JiraEventCallbackView, SlackCommandCallbackView
from . import views

urlpatterns = [
    url(r'^callbacks/event_slack', SlackEventCallbackView.as_view()),
    url(r'^callbacks/command_slack', SlackCommandCallbackView.as_view()),
    url(r'^callbacks/jira', JiraEventCallbackView.as_view()),
]
