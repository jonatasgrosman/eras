import requests
import json
import module.service.authService as AuthService
from module import config
from module.service.serviceException import ServiceException


def get_sentences(document):
    response = requests.post(config['NLP_HOST'] + '/tokenizer-postagger',
                             headers={'token': AuthService.get_token(), 'email': config['AUTHENTICATION_LOGIN']},
                             json=document)

    if not response.ok:
        raise ServiceException('NLP MODULE REQUEST ERROR')

    return json.loads(response.content.decode('utf-8'))['sentences']

