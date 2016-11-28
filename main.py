# -*- coding: utf-8 -*-
import vkrequests as vkr
import tensorflow as tf
import numpy as np
import os.path
import random
#import nltk
import time
import re

#from nltk.stem import WordNetLemmatizer

class Profiler():
	def __enter__(self):
		self._startTime = time.time()

	def __exit__(self, type, value, traceback):
		print('Время выполнения: {:.3f} с.'.format(time.time() - self._startTime))

def authorize():
	if os.path.exists('data/token.txt'):
		token = open('data/token.txt', 'r').read()

		if vkr.log_in(token=token):
			print('Успешная авторизация')
		else:
			print('Авторизация не удалась')

	else:
		while True:
			login = input('Логин: ')
			password = input('Пароль: ')
			new_token = vkr.log_in(login=login, password=password)
			if new_token:
				print('Успешная авторизация')
				open('data/token.txt', 'w').write(new_token)
				break
			else:
				print('Авторизация не удалась')

	global SELF_ID
	SELF_ID = vkr.get_user_id()

#print(vkr.get_user_id(link=input('Короткая ссылка на страницу друга: ')))

def message_getter(file):
	messages_list = vkr.get_messages_list()
	print('Обнаружено {} диалогов'.format(messages_list['count']))
	for k in range(messages_list['count']//200 + 1):

		for d in range(len(messages_list['items'])):
			msg_list = messages_list['items'][d]
			messages = vkr.get_messages(
				id=msg_list['user_id']
				)
			time.sleep(0.33)

			if 'chat_id' in msg_list:
				print('Сообщения из беседы, пропускаю')
				continue
			else:
				uname = vkr.get_user_name(
							uid=msg_list['user_id']
							)
				print('Сообщений в диалоге: {}::{}'.format(\
						messages['count'], uname
							)
						)

			for i in range(messages['count']//200 + 1):
				for j in range(len(messages['items'])):
					msg = messages['items'][j]
					if msg['body'] is not '':
						msg['body'] = re.sub(r'(https?://)?(m\.)?vk\.com/(.*)$', '__vkurl__', msg['body'])
						msg['body'] = re.sub(r'https?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),#%]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '__url__', msg['body'])
						file.write(
						'{} {}\n'.format(\
						'You' if msg['from_id'] == SELF_ID else 'Friend::{}::{}'.format(\
								msg['from_id'], uname),
								msg['body']
							)
						)	

				print('Iteration {}.{}'.format(i+1, len(messages['items'])))
				messages = vkr.get_messages(
					offset=(i+1)*200, id=msg_list['user_id']
				)
				time.sleep(0.33)

			print('Завершена обработка диалога №{}'.format((k)*200 + d+1))
		messages_list = vkr.get_messages_list(offset=(k+1)*200)

authorize()
if os.path.exists('data/message_dump.txt'):
	while True:
		ans = input('Файл с историей сообщений уже существует. Заменить его? (y/n) ')
		if ans.lower() == 'y' or ans.lower() == '':
			with open('data/message_dump.txt', 'a+') as f:
				f.seek(0)
				f.truncate()
				with Profiler():
					message_getter(f)
				break
		elif ans.lower() == 'n':
			break
		else:
			print('Неизвестный ответ.')

while True:
	ts, pts = vkr.get_long_poll_data()
	response = vkr.test(ts=ts,pts=pts)
	print(response)
	time.sleep(2)
#lemmatizer = WordNetLemmatizer()
