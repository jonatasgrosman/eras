import requests
from module import config


def get_token():
    response = requests.post(config['AUTHENTICATION_HOST'] + '/auth/authenticate',
                             json={'email': config['AUTHENTICATION_LOGIN'],
                                   'password': config['AUTHENTICATION_PASSWORD']})
    return response.json()['token']


def check_token(token, email):
    response = requests.get(config['AUTHENTICATION_HOST'] + '/auth/verify-token', headers={'token': token, 'email': email})
    if response.ok:
        return response.json()
