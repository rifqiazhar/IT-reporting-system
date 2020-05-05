from rest_framework.response import Response
from rest_framework import status


# def response_template(data=None, status=status.HTTP_200_OK, success=True, message_format=None):
#     return Response(status=status, data=message_format)

def response_template(data=None, status=status.HTTP_200_OK, success=True, message=[]):
    return Response(status=status, data=data)


def success_response(data):
    return response_template(data)
