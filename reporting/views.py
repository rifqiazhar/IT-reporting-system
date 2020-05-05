import json
import threading
from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from reporting.constant import JiraAPI, SlackAPI, FeatureSettingName
from reporting.models import ReportingHistory, FeatureSetting
from reporting.services import send_format_message_for_jira_card, preprocess_set_assigne, preprocess_set_status_card, \
    preprocess_jira_status, preprocess_jira_assigne
from reporting.utils import success_response
from rest_framework.status import (HTTP_400_BAD_REQUEST,
                                   HTTP_403_FORBIDDEN,
                                   HTTP_404_NOT_FOUND,
                                   HTTP_200_OK,
                                   HTTP_401_UNAUTHORIZED)

class LoggedResponse(Response):
    def __init__(self, **kwargs):
        super(LoggedResponse, self).__init__(**kwargs)
        kwargs['http_status_code'] = self.status_code


class SlackCommandCallbackView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        data = request.data
        if 'token' not in data or data['token'] != SlackAPI.COMMAND_TOKEN:
            return LoggedResponse(
                status=HTTP_401_UNAUTHORIZED,
                data={
                    "error": "Token invalid"
                })

        create_history = ReportingHistory.objects.create(
            requester_id=data['user_id'],
            requester_user_name=data['user_name'],
            channel_id=data['channel_id'],
            channel_name=data['channel_name'],
            message=data['text'],
        )
        message_format = {
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "will create card for {}, unique id {}".format(data['text'], create_history.id)
                    }
                },
            ]
        }
        t1 = threading.Thread(target=send_format_message_for_jira_card, args=(create_history.id,))
        t1.start()
        return success_response(data=message_format)


class SlackEventCallbackView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        data = request.data
        parsed_data = json.loads(data['payload'])
        if 'token' not in parsed_data or parsed_data['token'] != SlackAPI.COMMAND_TOKEN:
            return LoggedResponse(
                status=HTTP_401_UNAUTHORIZED,
                data={
                    "error": "Token invalid"
                })
        selected_option_value = parsed_data["actions"][0]["selected_option"]["value"]
        selected_option_display = parsed_data["actions"][0]["selected_option"]["text"]["text"]
        ts = parsed_data["message"]["ts"]
        jira_feature = FeatureSetting.objects.get(is_active=True,
                                                  feature_name=FeatureSettingName.JIRA_FEATURE_SETTING)
        if selected_option_display.lower() in jira_feature.parameters['statuses']:
            t1 = threading.Thread(target=preprocess_set_status_card,
                                  args=(selected_option_value, selected_option_display, ts,))
            t1.start()
        else:
            t1 = threading.Thread(target=preprocess_set_assigne,
                                  args=(selected_option_value, selected_option_display, ts,))
            t1.start()
        return success_response(None)


class JiraEventCallbackView(APIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        data = request.data
        issue = data['issue']
        jira_key = issue['key']
        change_log = data['changelog']
        if data["issue_event_type_name"] == JiraAPI.EVENT_WEBHOOK_ASSIGNE:
            user_id = change_log['items'][0]['to']
            user_display = change_log['items'][0]['toString']
            t1 = threading.Thread(target=preprocess_jira_assigne,
                                  args=(user_id, user_display, jira_key))
            t1.start()
        elif data["issue_event_type_name"] == JiraAPI.EVENT_WEBHOOK_GENERIC:
            status_change = change_log['items'][0]['toString']
            t1 = threading.Thread(target=preprocess_jira_status,
                                  args=(jira_key, status_change,))
            t1.start()
        return success_response(None)

    def get(self, request):
        data = request.data
        return success_response(None)
