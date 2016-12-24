# -*- coding: utf-8 -*-
import time

import vk

def vk_request_errors(request):
	def request_errors(*args, **kwargs):
		# response = request(*args, **kwargs); time.sleep(0.66)
		# Для вывода ошибки в консоль
		try:
			response = request(*args, **kwargs)
		except Exception as error:
			error = str(error)
			if 'Too many requests per second' in error or 'timed out' in error:
				time.sleep(0.33)
				return request_errors(*args, **kwargs)

			elif 'Failed to establish a new connection' in error:
				print('Check your connection!')

			elif 'incorrect password' in error:
				print('Incorrect password!')

			elif 'Read timed out' in error or 'Connection aborted' in error:
				print('WARNING\nResponse time exceeded!')
				time.sleep(0.66)
				return request_errors(*args, **kwargs)

			elif 'Failed loading' in error:
				raise

			elif 'Captcha' in error:
				print('Capthca!!!!!')
				#TODO обработать капчу

			elif 'Failed receiving session' in error:
				print('Error receiving session!')

			elif 'Auth check code is needed' in error:
				print('Auth code is needed!')

			else:
				if not api:
					print('Authentication required')
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
    scope = '69632' # messages, offline permissions
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
        api = vk.API(session, v='5.60')
        track_visitor()
    except UnboundLocalError: # session was not created
        raise Exception('Failed receiving session!')

    return session.access_token


@vk_request_errors
def get_long_poll_data():
    response = api.messages.getLongPollServer(need_pts='1')
    ts = response['ts']
    pts = response['pts']
    return response

@vk_request_errors
def get_new_messages(**kwargs):
    ts = kwargs.get('ts')
    pts = kwargs.get('pts')
    if not ts or not pts:
        new_ts, new_pts = get_long_poll_data()
    return api.messages.getLongPollHistory(
        ts=ts if ts else new_ts,
        pts=pts if pts else new_pts
    )


@vk_request_errors
def send_message(**kwargs):
    """
    """
    gid = None
    uid = kwargs.get('uid')
    if not uid:
        gid = kwargs['gid']
    text = kwargs['text']
    forward = kwargs.get('forward')
    rnd_id = kwargs['rnd_id']

    response = api.messages.send(
        peer_id=uid, message=text,
        forward_messages=forward,
        chat_id=gid, random_id=rnd_id
    )
    
    return response


@vk_request_errors
def get_messages_list(**kwargs):
    """
    """
    offset = str(kwargs.get('offset', '0'))
    count = '200'

    response = api.messages.getDialogs(
        count=count, offset=offset
        )
    return response


@vk_request_errors
def get_messages(**kwargs):
    """
    """
    count = '200'
    offset = str(kwargs.get('offset', '0'))
    friend_id = kwargs['uid']

    response = api.messages.getHistory(
        count=count, offset=offset,
        rev='1', user_id=friend_id
        )
    return response


@vk_request_errors
def get_user_name(**kwargs):
    uid = str(kwargs['uid'])

    if int(uid) < 0: # группа
        response = api.groups.getById(group_id=uid[1:])
        name = response[0]['name']
    else:
        response = api.users.get(user_ids=uid)
        name = response[0]['first_name'] + ' ' + response[0]['last_name']
    return name


@vk_request_errors
def get_user_id(**kwargs):
    user_link = kwargs.get('link')
    response = api.users.get(user_ids=user_link)
    return response[0]['id']


@vk_request_errors
def track_visitor():
    api.stats.trackVisitor()
