import module.service.authenticationService as AuthenticationService
import module.util.routeUtil as RouteUtil
from flask import request
from module import app
from module.service.serviceException import ServiceException


@app.route('/auth/authenticate', methods=['POST'])
@RouteUtil.safe_result()
def authenticate():
    try:
        return RouteUtil.data_to_json_response(AuthenticationService.authenticate(RouteUtil.safe_json_get('email'),
                                                                                  RouteUtil.safe_json_get('password')))
    except ServiceException:
        return 'INVALID USER/PASSWORD', 401


@app.route('/auth/verify-token', methods=['GET'])
@RouteUtil.safe_result()
def verify_token():
    try:
        return RouteUtil.data_to_json_response(AuthenticationService.verify_token(request.headers.get('email'),
                                                                                  request.headers.get('token')))
    except ServiceException:
        return 'INVALID TOKEN', 401


@app.route('/auth/refresh-token', methods=['GET'])
@RouteUtil.safe_result()
def refresh_token():
    try:
        return RouteUtil.data_to_json_response(AuthenticationService.refresh_token(request.headers.get('email'),
                                                                                   request.headers.get('token')))
    except ServiceException:
        return 'INVALID TOKEN', 401
