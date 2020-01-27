import module.service.authenticationService as AuthenticationService
import module.service.emailService as EmailService
import module.util.routeUtil as RouteUtil
from flask import request, g
from module import app, config
from module.service.serviceException import ServiceException


@app.route('/user', methods=['GET', 'POST', 'DELETE'])
@RouteUtil.safe_result()
@RouteUtil.restrict(['ADMIN', 'USER', 'MODULE', 'COLLABORATOR'])
def user():
    user_email = request.args.get('email')

    if request.method == 'GET':

        # common user only can see your own details
        if g.user['role'] == 'USER':
            return RouteUtil.data_to_json_response(AuthenticationService.get_user(g.user['email']))

        if user_email:
            return RouteUtil.data_to_json_response(AuthenticationService.get_user(user_email))
        else:
            return RouteUtil.data_to_json_response(AuthenticationService.get_users())

    elif request.method == 'POST':

        if user_email:  # update

            # common user only can update your own details and cannot change your role
            if g.user['role'] == 'USER':
                AuthenticationService.update_user(g.user['email'],
                                                  RouteUtil.safe_json_get('firstName'),
                                                  RouteUtil.safe_json_get('lastName'),
                                                  g.user['role'])
            else:
                AuthenticationService.update_user(RouteUtil.safe_json_get('email'),
                                                  RouteUtil.safe_json_get('firstName'),
                                                  RouteUtil.safe_json_get('lastName'),
                                                  RouteUtil.safe_json_get('role'))

            return 'USER UPDATED', 200

        else:  # insert

            if g.user['role'] == 'USER':
                return 'INVALID ROLE', 403

            temporary_token = AuthenticationService.insert_user(RouteUtil.safe_json_get('email'),
                                                                RouteUtil.safe_json_get('firstName'),
                                                                RouteUtil.safe_json_get('lastName'),
                                                                RouteUtil.safe_json_get('role'))

            recovery_url = config['RECOVERY_PASSWORD_PAGE_URL'] + '?token=' + temporary_token + \
                           '&email=' + RouteUtil.safe_json_get('email')

            message = config['EMAIL_HEADER']
            message += '<div style="height:200px; padding:50px;">'
            message += '<p>Hi ' + RouteUtil.safe_json_get('firstName') + ',</p>'
            message += config['WELCOME_EMAIL_MESSAGE']
            message += '<p><a href="' + recovery_url + '">' + recovery_url + '</a></p>'
            message += '</div>'
            message += config['EMAIL_FOOTER']

            EmailService.send(config['WELCOME_EMAIL_SUBJECT'], [RouteUtil.safe_json_get('email')], message)

            return 'USER INSERTED', 200

    elif request.method == 'DELETE':

        if g.user['role'] == 'USER':
            return 'INVALID ROLE', 403

        AuthenticationService.remove_user(user_email)
        return 'USER REMOVED', 200


@app.route('/user/change-password', methods=['POST'])
@RouteUtil.restrict(['ADMIN', 'USER', 'MODULE', 'COLLABORATOR'])
@RouteUtil.safe_result()
def change_password():
    try:
        AuthenticationService.update_user_password(g.user['email'],
                                                   RouteUtil.safe_json_get('currentPassword'),
                                                   RouteUtil.safe_json_get('newPassword'))
        return 'PASSWORD CHANGED', 200
    except ServiceException:
        return 'WRONG PASSWORD', 401


@app.route('/user/reset-password', methods=['POST'])
def reset_password():
    try:
        AuthenticationService.update_user_password(RouteUtil.safe_json_get('email'),
                                                   RouteUtil.safe_json_get('token'),
                                                   RouteUtil.safe_json_get('newPassword'), True)
        return 'PASSWORD CHANGED', 200
    except ServiceException:
        return 'INVALID TOKEN', 401


@app.route('/user/recovery-password', methods=['GET'])
def recovery_password():
    user_email = request.args.get('email')

    if user_email:
        temporary_token, subject_user = AuthenticationService.get_temporary_token(user_email)

        if temporary_token:
            recovery_url = config['RECOVERY_PASSWORD_PAGE_URL']+'?token='+temporary_token + '&email=' + user_email

            message = config['EMAIL_HEADER']
            message += '<div style="height:200px; padding:50px;">'
            message += '<p>Hi ' + subject_user['firstName'] + ',</p>'
            message += config['RECOVERY_PASSWORD_EMAIL_MESSAGE']
            message += '<p><a href="' + recovery_url + '">' + recovery_url + '</a></p>'
            message += '</div>'
            message += config['EMAIL_FOOTER']

            EmailService.send(config['RECOVERY_PASSWORD_EMAIL_SUBJECT'], [user_email], message)

            return 'EMAIL SENT', 200
        else:
            return 'INVALID USER', 400
    else:
        return 'INVALID REQUEST', 400
