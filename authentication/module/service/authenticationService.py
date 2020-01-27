from calendar import timegm
from datetime import datetime
from jose import jwt, JWTError
from module import config
from module import db
from module.service.serviceException import ServiceException
from module.util.mongoUtil import mongo_result_wrapper


def check_user(email, keep_password=False, keep_temporary_token=False):

    if not email:
        raise ServiceException('INVALID USER EMAIL')

    user = get_user(email, keep_password, keep_temporary_token)

    if not user:
        raise ServiceException('INVALID USER EMAIL')

    return user


def insert_user(email, first_name, last_name, role):

    if not email:
        raise ServiceException('Email is required')

    user = get_user(email)

    if user:
        raise ServiceException('User already exists')

    now = timegm(datetime.utcnow().utctimetuple())

    payload = {
        'iat': now,
        'exp': now + config['JWT_DELTA_LONG_EXPIRATION'],
        'sub': email,
        'sub_role': role,
        'sub_firstName': first_name,
        'sub_lastName': last_name
    }
    token = jwt.encode(payload, config['JWT_SECRET_KEY'], algorithm=config['JWT_ALGORITHM'])

    db.users.insert_one({
        'email': email,
        'firstName': first_name,
        'lastName': last_name,
        'role': role,
        'temporaryToken': token
    })

    return token


def update_user_password(email, key, new_password, key_is_token=False):

    user = check_user(email, True, True)

    if key_is_token:
        try:
            if 'temporaryToken' in user and user['temporaryToken'] == key:
                verify_token(email, key)
            else:
                raise ServiceException('Invalid token')
        except ServiceException:
            raise ServiceException('Invalid token')
    elif config['CIPHER'].decrypt(user['password']) != key:
        raise ServiceException('Invalid old password')

    db.users.update_one({
        'email': email
    }, {
        '$set': {
            'password': config['CIPHER'].encrypt(new_password),
            'lastPasswordUpdate': datetime.utcnow()
        },
        '$unset': {
            'temporaryToken': 1
        }
    })


def get_temporary_token(email):

    user = check_user(email)

    now = timegm(datetime.utcnow().utctimetuple())

    payload = {
        'iat': now,
        'exp': now + config['JWT_DELTA_LONG_EXPIRATION'],
        'sub': email,
        'sub_role': user['role'],
        'sub_firstName': user['firstName'],
        'sub_lastName': user['lastName']
    }
    token = jwt.encode(payload, config['JWT_SECRET_KEY'], algorithm=config['JWT_ALGORITHM'])

    db.users.update_one({
        'email': email
    }, {
        '$set': {
            'temporaryToken': token
        }
    })

    return token, user


def update_user(email, first_name, last_name, role):

    check_user(email)

    db.users.update_one({
        'email': email
    }, {
        '$set': {
            'firstName': first_name,
            'lastName': last_name,
            'role': role
        }
    })


def remove_user(email):

    check_user(email)

    db.users.delete_one({
        'email': email
    })


@mongo_result_wrapper()
def get_users():

    return db.users.aggregate([
        {'$match': {}},
        {'$project': {
            '_id': 0,
            'email': 1,
            'firstName': 1,
            'lastName': 1,
            'role': 1
        }}
    ])


@mongo_result_wrapper(is_single_result=True)
def get_user(email, keep_password=False, keep_temporary_token=False):

    project = {
        '_id': 0,
        'email': 1,
        'firstName': 1,
        'lastName': 1,
        'role': 1
    }

    if keep_password:
        project['password'] = '$password'
    if keep_temporary_token:
        project['temporaryToken'] = '$temporaryToken'

    return db.users.aggregate([
        {'$match': {'email': email}},
        {'$project': project}
    ])


def authenticate(email, password):

    user = check_user(email, True)

    if config['CIPHER'].decrypt(user['password']) == password:
        now = timegm(datetime.utcnow().utctimetuple())

        payload = {
            'iat': now,
            'exp': now + config['JWT_DELTA_EXPIRATION'],
            'sub': user['email'],
            'sub_role': user['role'],
            'sub_firstName': user['firstName'],
            'sub_lastName': user['lastName']
        }
        token = jwt.encode(payload, config['JWT_SECRET_KEY'], algorithm=config['JWT_ALGORITHM'])

        db.users.update_one({
            'email': email
        }, {
            '$set': {
                'lastAuthentication': datetime.utcnow()
            }
        })

        return {
            'email': user['email'],
            'role': user['role'],
            'firstName': user['firstName'],
            'lastName': user['lastName'],
            'token': token
        }
    else:
        raise ServiceException('Invalid password')


def verify_token(email, token):

    check_user(email)

    try:

        user = jwt.decode(token, config['JWT_SECRET_KEY'], algorithms=config['JWT_ALGORITHM'], subject=email)
        return {
            'email': user['sub'],
            'role': user['sub_role'],
            'firstName': user['sub_firstName'],
            'lastName': user['sub_lastName'],
            'token': token
        }

    except JWTError:
        raise ServiceException('Invalid token')


def refresh_token(email, token):

    user = check_user(email)

    try:
        verify_token(email, token)
    except ServiceException:
        raise ServiceException('Invalid token')

    now = timegm(datetime.utcnow().utctimetuple())  # now in seconds

    payload = {
        'iat': now,
        'exp': now + config['JWT_DELTA_EXPIRATION'],
        'sub': user['email'],
        'sub_role': user['role'],
        'sub_firstName': user['firstName'],
        'sub_lastName': user['lastName']
    }
    token = jwt.encode(payload, config['JWT_SECRET_KEY'], algorithm=config['JWT_ALGORITHM'])

    return {
        'email': user['email'],
        'role': user['role'],
        'firstName': user['firstName'],
        'lastName': user['lastName'],
        'token': token
    }
