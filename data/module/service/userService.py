import requests
import json
import module.service.authService as AuthService
from module import config
from module.service.serviceException import ServiceException


def get_user(email):
    response = requests.get(config['AUTHENTICATION_HOST'] + '/user?email='+email,
                            headers={'token': AuthService.get_token(), 'email': config['AUTHENTICATION_LOGIN']})
    return json.loads(response.content.decode('utf-8'))


def append_user_details(user, append_role=False):

    if 'email' not in user:
        raise ServiceException('EMAIL IS REQUIRED!')

    detailed_user = get_user(user['email'])

    if not detailed_user:
        raise ServiceException('USER NOT FOUND')

    user['firstName'] = detailed_user['firstName']
    user['lastName'] = detailed_user['lastName']

    if append_role:
        user['role'] = detailed_user['role']

    return user
