# -*- coding: utf-8 -*-
import vkrequests as vkr
import os.path
import time

#import tensorflow as tf

class Profiler():
	def __enter__(self):
		self._startTime = time.time()

	def __exit__(self, type, value, traceback):
		print(u'Время выполнения: {:.3f} с.'.format(time.time() - self._startTime))

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
	SELF_ID = vkr.get_user_id()

authorize()

#vkr.FRIEND_ID = vkr.get_user_id(link=input(u'Короткая ссылка на страницу друга: '))
#print(vkr.FRIEND_ID)

with open('data/message_dump.txt', 'a+') as f:
	messages_list = vkr.get_messages_list()
	print(u'Обнаружено {} диалогов'.format(messages_list['count']))
	for k in range(messages_list['count']//200 + 1):

		for d in range(len(messages_list['items'])):
			messages = vkr.get_messages(
				id=messages_list['items'][d]['user_id']
				)
			time.sleep(0.33)

			if 'chat_id' in messages_list['items'][d]:
				print(u'Сообщения из беседы, пропускаю')
				continue
			else:
				print(
					u'Сообщений в диалоге: {}::{}'.format(\
						messages['count'],
						vkr.get_user_name(
							uid=messages_list['items'][d]['user_id']
							)
						)
					)

			for i in range(messages['count']//200 + 1):
				for j in range(len(messages['items'])):
					if messages['items'][j]['body'] is not '':
						try:
							f.write(
								'{} {}\n'.format(\
								'You' if messages['items'][j]['from_id'] == SELF_ID else 'Friend',
								messages['items'][j]['body']
								)
							)
						except UnicodeEncodeError: # problem with emoji on win
							print('Warning {}.{}'.format(i,j))

				print('Iteration {}.{}'.format(i+1, len(messages['items'])))
			messages = vkr.get_messages(
				offset=(i+1)*200, id=messages_list['items'][d]['user_id']
				)
			time.sleep(0.33)

			print(u'Завершена обработка диалога №{}'.format((k)*200 + d+1))
		messages_list = vkr.get_messages_list(offset=(k+1)*200)
		
