import json
import re
import logging
import module.service.authenticationService as AuthenticationService
from functools import wraps, update_wrapper
from datetime import datetime
from bson import json_util
from flask import request, g, Response, make_response
from module import app


def nocache(view):
    @wraps(view)
    def no_cache(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers['Last-Modified'] = datetime.now()
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        return response

    return update_wrapper(no_cache, view)


def restrict(roles):
    def wrapper(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):

            try:

                if hasattr(g, 'user'):
                    return f(*args, **kwargs)

                token = request.headers.get('token')
                email = request.headers.get('email')

                if not token or not email:
                    token = request.args.get('token')
                    email = request.args.get('email')

                if token and email:

                    user = AuthenticationService.verify_token(email, token)

                    if user:
                        if user['role'] in roles:
                            g.user = user
                            return f(*args, **kwargs)
                        else:
                            return 'INVALID ROLE', 403

                return 'UNAUTHORIZED', 401

            except Exception as e:
                app.logger.error(e)
                return 'MAYDAY! MAYDAY!', 500

        return decorated_function
    return wrapper


def safe_result():
    def wrapper(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except Exception as e:

                logging.error(
                    """
                        Request:   {method} {path}
                        IP:        {ip}
                        User:      {user}
                        Agent:     {agent_platform} | {agent_browser} {agent_browser_version}
                        Raw Agent: {agent}
                        Exception: {exception}
                    """.format(
                        method= request.method,
                        path= request.path,
                        ip= request.remote_addr,
                        agent_platform= request.user_agent.platform,
                        agent_browser= request.user_agent.browser,
                        agent_browser_version= request.user_agent.version,
                        agent= request.user_agent.string,
                        user= g.user['email'] if hasattr(g, 'user') else '',
                        exception=e
                    ), exc_info=True
                )

                return 'MAYDAY! MAYDAY!', 500
        return decorated_function
    return wrapper


def data_to_json_response(data, if_none_not_found=False):
    if not data and if_none_not_found:
        return 'NOT FOUND', 404
    else:
        return Response(json.dumps(data, default=json_util.default), mimetype='application/json')


def safe_json_get(key):
    if request.json and key in request.json:
        return request.json[key]


def value_to_boolean(value):
    return value and bool(re.match('^[yY]es$|^[Tt]rue$', value))
