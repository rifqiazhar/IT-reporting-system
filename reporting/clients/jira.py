import requests
from requests.auth import HTTPBasicAuth
import json

from reporting.constant import JiraAPI
from reporting.models import ReportingHistory

auth = HTTPBasicAuth(JiraAPI().USERNAME, JiraAPI().TOKEN)
url = JiraAPI().BASE_URL
headers = {
    "Accept": "application/json",
    "Content-Type": "application/json"
}


def create_card(description, jira_base_url):
    relative_url = url + "/rest/api/3/issue"
    splited = description.split(" ")
    title = ""
    for i in range(3):
        try:
            title += splited[i] + " "
        except Exception:
            continue
    card = json.dumps({
        "fields": {
            "project": {
                "key": "IS"
            },
            "summary": title,
            "description": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [
                            {
                                "text": description,
                                "type": "text"
                            }
                        ]
                    }
                ]
            },
            "issuetype": {
                "name": "Task"
            }

        }

    })
    response = requests.request(
        "POST",
        relative_url,
        data=card,
        headers=headers,
        auth=auth
    )
    created_card = json.loads(response.text)
    card_key = created_card['key']
    jira_link = jira_base_url + card_key
    project_key = card_key.split('-')[0]
    return card_key, jira_link, project_key


def get_assigne_users(project_key):
    relative_url = url + "/rest/api/3/user/assignable/search?project={}".format(project_key)
    response = requests.request(
        "GET",
        relative_url,
        auth=auth
    )
    users = json.loads(response.text)
    list_user = []
    for user in users:
        data = {
                   "text": {
                       "type": "plain_text",
                       "text": user['displayName'],
                       "emoji": True
                   },
                   "value": user['accountId']
               }
        list_user.append(data)
    return list_user


def set_assigne_users(user_id, card_key):
    relative_url = url + "/rest/api/3/issue/{}/assignee".format(card_key)
    data = json.dumps({
        "accountId": user_id
    })
    response = requests.request(
        "PUT",
        relative_url,
        data=data,
        headers=headers,
        auth=auth
    )
    if response.status_code == 204:
        return True
    else:
        return False


def get_card_statuses(card_key):
    relative_url = url + "/rest/api/3/issue/{}/transitions".format(card_key)
    response = requests.request(
        "GET",
        relative_url,
        auth=auth
    )
    data = json.loads(response.text)["transitions"]
    statuses = []
    for status in data:
        data = {
            "text": {
                "type": "plain_text",
                "text": status['name'],
                "emoji": True
            },
            "value": status['id']
        }
        statuses.append(data)
    return statuses


def set_card_statuses(card_key, status_id):
    relative_url = url + "/rest/api/3/issue/{}/transitions".format(card_key)
    data = json.dumps({"transition": {"id": status_id}})
    response = requests.request(
        "POST",
        relative_url,
        data=data,
        headers=headers,
        auth=auth
    )
    if response.status_code == 204:
        return True
    else:
        return False
