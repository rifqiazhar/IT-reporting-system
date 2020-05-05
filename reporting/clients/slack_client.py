from datetime import date

import requests
import json
import slack

from reporting.models import ReportingHistory

# bot
slack_client_api = slack.WebClient(
    token="xoxp-32269231124-666943983061-857301558005-fca9e1fac3f4bf56facf89025ac60e70",
)
# try as User
# slack_client_api = slack.WebClient(
#     token="xoxp-32269231124-666943983061-694058704770-5edcd31cf4c7f0ac928e536cfca11089",
# )

def message_with_webhook(message):
    data = json.dumps({"text": message})
    headers = {
        "Content-Type": "application/json"
    }
    url = "https://hooks.slack.com/services/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"
    response = requests.request(
        "POST",
        url,
        data=data,
        headers=headers
    )


def send_message_with_jiracard(reporting_history, message_format):
    channel = reporting_history.channel_id
    response = slack_client_api.chat_postMessage(
        channel=channel,
        text="unique id :{}".format(reporting_history.id),
        blocks=json.dumps(message_format)
    )
    return response


def update_message(slack_ts, reporting_history, message_format):
    response = slack_client_api.chat_update(
        channel=reporting_history.channel_id,
        text="Update message",
        ts=slack_ts,
        blocks=json.dumps(message_format)
    )
    return response
