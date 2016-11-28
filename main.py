# -*- coding: utf-8 -*-
import vkrequests as vkr
import tensorflow as tf
import numpy as np
import os.path
import random
import nltk
import time
import re

from nltk.stem import WordNetLemmatizer

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
		while True:
			login = input('Логин: ')
			password = input('Пароль: ')
			token = vkr.log_in(login=login, password=password)

			if token:
				print(u'Успешная авторизация')
				open('data/token.txt', 'w').write(token)
				break
			else:
				print(u'Авторизация не удалась')

	global SELF_ID
	SELF_ID = vkr.get_user_id()

#print(vkr.get_user_id(link=input(u'Короткая ссылка на страницу друга: ')))

def message_getter(file):
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
				uname = vkr.get_user_name(
							uid=messages_list['items'][d]['user_id']
							)
				print(u'Сообщений в диалоге: {}::{}'.format(\
						messages['count'], uname
							)
						)

			for i in range(messages['count']//200 + 1):
				for j in range(len(messages['items'])):
					if messages['items'][j]['body'] is not '':
						try:
							file.write(
							'{} {}\n'.format(\
							'You' if messages['items'][j]['from_id'] ==\
								SELF_ID else 'Friend::{}::{}'.format(\
									messages['items'][j]['from_id'], uname
									),
								messages['items'][j]['body']
								)
							)
						except UnicodeEncodeError: # problem with emoji on win
							import sys
							reload(sys)
							sys.setdefaultencoding('utf-8')
							file.write(
							'{} {}\n'.format(\
							'You' if messages['items'][j]['from_id'] ==\
								SELF_ID else 'Friend::{}::{}'.format(\
									messages['items'][j]['from_id'], uname
									),
								messages['items'][j]['body']
								)
							)

				print('Iteration {}.{}'.format(i+1, len(messages['items'])))
				messages = vkr.get_messages(
					offset=(i+1)*200, id=messages_list['items'][d]['user_id']
					)
				time.sleep(0.33)

			print(u'Завершена обработка диалога №{}'.format((k)*200 + d+1))
		messages_list = vkr.get_messages_list(offset=(k+1)*200)

authorize()
if os.path.exists('data/message_dump.txt'):
	while True:
		ans = input(u'Файл с историей сообщений уже существует. Заменить его? (y/n) ')
		if ans.lower() == 'y':
			with open('data/message_dump.txt', 'a+') as f:
				f.seek(0)
				f.truncate()
				message_getter(f)
				break
		elif ans.lower() == 'n':
			break
		else:
			print(u'Неизвестный ответ.')

lemmatizer = WordNetLemmatizer()
