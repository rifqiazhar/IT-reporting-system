from datetime import date
from django.utils import timezone

from reporting.clients.jira import create_card, get_assigne_users, set_assigne_users, get_card_statuses, \
    set_card_statuses
from reporting.clients.slack_client import send_message_with_jiracard, update_message
from reporting.models import ReportingHistory


def send_format_message_for_jira_card(reporting_id):
    reporting_history = ReportingHistory.objects.get(pk=reporting_id)
    if reporting_history:
        jira_key, url, project_key = create_card(reporting_history.message,
                                                 "https://itsupportkpjulo.atlassian.net/browse/")
        jira_users = get_assigne_users(project_key)
        statuses = get_card_statuses(jira_key)
        converted_date_cdate =date.strftime(timezone.localtime(reporting_history.cdate), '%d-%b-%Y %H:%M')
        converted_date_udate =date.strftime(timezone.localtime(reporting_history.udate), '%d-%b-%Y %H:%M')
        message_format = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "New Card created by @{}:\n*<{}|Jira Card - {}>*".format(
                        reporting_history.requester_user_name, url, jira_key)
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": "*Type:*\n`Task`"
                    },
                    {
                        "type": "mrkdwn",
                        "text": "*When:*\n{}".format(converted_date_cdate)
                    },
                    {
                        "type": "mrkdwn",
                        "text": "*Last Update:*\n{}".format(converted_date_udate)
                    },
                    # {
                    #     "type": "mrkdwn",
                    #     "text": "*Status:*\n`TO DO`"
                    # },
                    {
                        "type": "mrkdwn",
                        "text": "*Specs:*\n{}".format(reporting_history.message)
                    }
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Set Card Status"
                },
                "accessory": {
                    "type": "static_select",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "TO DO",
                        "emoji": True
                    },
                    "options": statuses
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Pick assigned user"
                },
                "accessory": {
                    "type": "static_select",
                    "placeholder": {
                        "type": "plain_text",
                        "text": "Assign user",
                        "emoji": True
                    },
                    "options": jira_users
                }
            }
        ]
        response = send_message_with_jiracard(reporting_history, message_format)
        reporting_history.update_safely(message_slack_ts=response['ts'],
                                        jira_card_id=jira_key,
                                        jira_status="TO DO")


def update_message_slack_for_jira(slack_ts, selected_display_name, change_status):
    reporting_history = ReportingHistory.objects.get(message_slack_ts=slack_ts)
    if reporting_history:
        url = "https://itsupportkpjulo.atlassian.net/browse/{}".format(reporting_history.jira_card_id)
        jira_users = get_assigne_users(reporting_history.jira_card_id.split('-')[0])
        statuses = get_card_statuses(reporting_history.jira_card_id)
        current_assignee = reporting_history.user_assignee_display or 'Pick assigned user'
        current_status_card = reporting_history.jira_status or 'Set Card Status'
        if change_status == "assignee":
            current_assignee = selected_display_name
        else:
            current_status_card = selected_display_name
        converted_date_cdate = date.strftime(timezone.localtime(reporting_history.cdate), '%d-%b-%Y %H:%M')
        converted_date_udate = date.strftime(timezone.localtime(reporting_history.udate), '%d-%b-%Y %H:%M')

        message_format = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "New Card created by @{}:\n*<{}|Jira Card - {}>*".format(
                        reporting_history.requester_user_name, url, reporting_history.jira_card_id)
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": "*Type:*\n`Task`"
                    },
                    {
                        "type": "mrkdwn",
                        "text": "*When:*\n{}".format(converted_date_cdate)
                    },
                    {
                        "type": "mrkdwn",
                        "text": "*Last Update:*\n{}".format(converted_date_udate)
                    },
                    {
                        "type": "mrkdwn",
                        "text": "*Specs:*\n{}".format(reporting_history.message)
                    }
                ]
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Set Card Status"
                },
                "accessory": {
                    "type": "static_select",
                    "placeholder": {
                        "type": "plain_text",
                        "text": current_status_card,
                        "emoji": True
                    },
                    "options": statuses
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Pick assigned user"
                },
                "accessory": {
                    "type": "static_select",
                    "placeholder": {
                        "type": "plain_text",
                        "text": current_assignee,
                        "emoji": True
                    },
                    "options": jira_users
                }
            }
        ]
        update_message(slack_ts, reporting_history, message_format)


def preprocess_set_assigne(user_id, selected_user_display, slack_ts):
    reporting_history = ReportingHistory.objects.get(message_slack_ts=slack_ts)
    if reporting_history:
        card_key = reporting_history.jira_card_id
        assign_success = set_assigne_users(user_id, card_key)
        if assign_success:
            update_message_slack_for_jira(slack_ts, selected_user_display, 'assignee')
            reporting_history.update_safely(user_assignee_id=user_id,
                                            user_assignee_display=selected_user_display)


def preprocess_set_status_card(selected_status_id, selected_status_display, slack_ts):
    reporting_history = ReportingHistory.objects.get(message_slack_ts=slack_ts)
    if reporting_history:
        card_key = reporting_history.jira_card_id
        change_status_success = set_card_statuses(card_key, selected_status_id)
        if change_status_success:
            # update_message_slack_for_jira(slack_ts, selected_status_display, 'change_status_card')
            reporting_history.update_safely(jira_status=selected_status_display)


def preprocess_jira_status(jira_key, new_selected_status):
    reporting_history = ReportingHistory.objects.get(jira_card_id=jira_key)
    if reporting_history:
        update_message_slack_for_jira(reporting_history.message_slack_ts,
                                      new_selected_status, 'change_status_card')
        reporting_history.update_safely(jira_status=new_selected_status)


def preprocess_jira_assigne(user_id, selected_user_display, jira_key):
    reporting_history = ReportingHistory.objects.get(jira_card_id=jira_key)
    if reporting_history:
        assign_success = set_assigne_users(user_id, jira_key)
        if assign_success:
            update_message_slack_for_jira(reporting_history.message_slack_ts,
                                          selected_user_display, 'assignee')
            reporting_history.update_safely(user_assignee_id=user_id,
                                            user_assignee_display=selected_user_display)
