# -*- coding: utf-8 -*-
import time

from libs import vk

api = None

MARAT_ID = '183338574' # модель будет обучаться на ответах Марату

def vk_request_errors(request):
    def request_errors(*args, **kwargs):
        # Для вывода ошибки в консоль
        # response = request(*args, **kwargs); time.sleep(0.66)
        try:
            response = request(*args, **kwargs)
        except Exception as error:
            error = str(error)
            if 'Too many requests per second' in error:
                print('sleeping')
                time.sleep(2)
                return request_errors(*args, **kwargs)

            elif 'Failed to establish a new connection' in error:
                print('Check your connection!')

            elif 'incorrect password' in error:
                print('Incorrect password!')

            elif 'Read timed out' in error:
                print('Response time exceeded!')

            elif 'Captcha' in error:
                print('Capthca!!!!!')
                # raise #TODO обработать капчу

            elif 'Failed receiving session' in error:
                print('Error receiving session!')

            elif 'Auth check code is needed' in error:
                print('Auth code is needed!')

            else:
                print('\nERROR! ' + error + '\n')

            return False
        else:
            return response
    return request_errors


@vk_request_errors
def log_in(**kwargs):
    # vk.logger.setLevel('DEBUG')
    """
    :token:
    :key:
    :login:
    :password:

    :return: string ( token )
    """
    scope = '4096' # messages permission
    app_id = '5746984'

    token = kwargs.get('token')
    key = str(kwargs.get('key'))

    if token:
        session = vk.AuthSession(
            access_token=token, scope=scope, app_id=app_id
        )
    elif key:
        login, password = kwargs['login'], kwargs['password']
        session = vk.AuthSession(
            user_login=login, user_password=password,
            scope=scope, app_id=app_id, key=key
        )
    else:
        login, password = kwargs['login'], kwargs['password']
        session = vk.AuthSession(
            user_login=login, user_password=password,
            scope=scope, app_id=app_id
        )

    global api
    try:
        api = vk.API(session, v='5.6')
    except UnboundLocalError: # session was not created
        raise Exception('Failed receiving session!')

        track_visitor()

    return session.access_token


@vk_request_errors
def get_messages(**kwargs):
    """
    """
    m_count = str(kwargs.get('count', '200'))
    offset = str(kwargs.get('offset', '0'))

    response = api.messages.getHistory(
        count=m_count, offset=offset,
        rev='1', user_id=MARAT_ID
        )
    return response


@vk_request_errors
def get_self_id():
    response = api.users.get()
    return response[0]['id']


@vk_request_errors
def track_visitor():
    api.stats.trackVisitor()
