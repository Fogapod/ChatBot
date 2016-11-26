# -*- coding: utf-8 -*-
#import tensorflow as tf
import vkrequests as vkr
import os.path

def authorize():
	if os.path.exists('data/token.txt'):
		token = open('data/token.txt', 'r').read()

		if vkr.log_in(token=token):
			print(u'Успешная авторизация')
		else:
			print(u'Авторизация не удалась')

	else:
		login = input('Логин: ')
		password = input('Пароль: ')
		token = vkr.log_in(login=login, password=password)

		if token:
			print(u'Успешная авторизация')
			open('data/token.txt', 'w').write(token)
		else:
			print(u'Авторизация не удалась')
	global SELF_ID
	SELF_ID = vkr.get_self_id()

authorize()

with open('data/message_dump.txt', 'a+') as f:
	messages = vkr.get_messages()
	for i in range(messages['count']//200 + 1):
		for j in range(len(messages['items'])):
			if messages['items'][j]['body'] is not '':
				try:
					f.write(
						'{} {}\n'.format(\
						'You' if messages['items'][j]['from_id'] == SELF_ID else 'Companion',
						messages['items'][j]['body']
										)
					)
				except UnicodeEncodeError: # problem with emoji on win
					print('Warning {}.{}'.format(i,j))
		print('Iteration {}.{}'.format(i+1, len(messages['items'])))
		messages = vkr.get_messages(offset=(i+1)*200)