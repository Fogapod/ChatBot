# -*- coding: utf-8 -*-
import vkrequests as vkr
#import tensorflow as tf
from io import BytesIO
import numpy as np
import os.path
import random
import pycurl
import time
import json
import re



class Profiler():
	def __enter__(self):
		self._startTime = time.time()

	def __exit__(self, type, value, traceback):
		print('Время выполнения: {:.3f} с.'.format(time.time() - self._startTime))

#print(vkr.get_user_id(link=input('Короткая ссылка на страницу друга: ')))

class Client:
	def __init__(self):
		self.STREAM_URL = 'https://{}?act={}&key={}&ts={}&wait={}&mode={}&version={}'
		self.SELF_ID = None

	def authorize(self):
		if os.path.exists('data/token.txt'):
			token = open('data/token.txt', 'r').read()
			if token:
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

		self.SELF_ID = vkr.get_user_id()

	def message_getter(self, file):
		#TODO: распознование стикеров
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
					file.write('### {}::{}\n'.format(uname, msg_list['user_id']))

				for i in range(messages['count']//200 + 1):
					for j in range(len(messages['items'])):
						msg = messages['items'][j]
						text = msg['body']
						if text is not '':
							text = re.sub(r'(https?://)?(?:m\.)?(v)(k)\.com/(?:.*)', '__vkurl__', text.lower())
							text = re.sub(r'''(?i)\b((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|(([^\s()<>]+|(([^\s()<>]+)))*))+(?:(([^\s()<>]+|(([^\s()<>]+)))*)|[^\s`!()[]{};:'".,<>?«»“”‘’]))''', '__url__', text)
							file.write(
							'{} {}\n'.format(\
								':You:' if msg['from_id'] == self.SELF_ID else ':Friend:',
								text
								)
							)	

					print('Iteration {}.{}'.format(i+1, len(messages['items'])))
					messages = vkr.get_messages(
						offset=(i+1)*200, id=msg_list['user_id']
					)
					time.sleep(0.33)
				file.write('### {}::{}\n\n'.format(uname, msg_list['user_id']))
				print('Завершена обработка диалога №{}'.format((k)*200 + d+1))
			messages_list = vkr.get_messages_list(offset=(k+1)*200)

	def set_url(self, server, key, ts, act='a_check', wait=30, mode=128, v=1):
		url = self.STREAM_URL.format(server, act, key, ts, wait, mode, v)
		return url

client = Client()

client.authorize()
if os.path.exists('data/message_dump.txt'):
	while True:
		ans = input('Файл с историей сообщений уже существует. Заменить его? (y/n) ')
		if ans.lower() == 'y' or ans == '':
			with open('data/message_dump.txt', 'a+') as f:
				f.seek(0)
				f.truncate()
				with Profiler():
					client.message_getter(f)
				break
		elif ans.lower() == 'n':
			break
		else:
			print('Неизвестный ответ.')
else:
	with open('data/message_dump.txt', 'a+') as f:
		client.message_getter(f)

last_rnd_id = 0

lpd = vkr.get_long_poll_data()
url = client.set_url(
lpd['server'],
lpd['key'],
lpd['ts']
)

c = pycurl.Curl()
m = pycurl.CurlMulti()
print('-'*5 + 'Начинаю слушать long poll' + '-'*5)
while True:
	s = BytesIO()
	c.setopt(c.URL, url)
	c.setopt(c.WRITEFUNCTION, s.write)
	m.add_handle(c)

	while True:
		ret, num_handles = m.perform()
		if ret != pycurl.E_CALL_MULTI_PERFORM:
			break

	while num_handles:
		time.sleep(1)
		while 1:
			ret, num_handles = m.perform()
			if ret != pycurl.E_CALL_MULTI_PERFORM:
				break
	response = s.getvalue().decode('utf-8')
	response = json.loads(response)

	m.remove_handle(c)

	print(response)

	url = client.set_url(
		lpd['server'],
		lpd['key'],
		response['ts']
	)

	for update in response['updates']:
		if update[0] is 4 and update[7] != last_rnd_id and update[3]:
			text = update[6]
			if text.lower() == 'ершов' or\
					text.lower() == 'женя' or\
					text.lower() == 'жень' or\
					text.lower() == 'женька' or\
					text.lower() == 'жека':
				text = 'А'
			elif re.sub('^( )*', '', text).startswith('/'):
				text = text[1:]
				if re.match('^(скажи)|(say) ', text.lower()):
					text = re.sub('^((скажи)|(say)) ', '', text.lower())
					text = re.search('(^(.*)\Wto)|(^(.*)\W?/)', text).group()
					text = re.sub('\W(.*)$', '', text)
				else:
					text = 'Попка молодец🐔' if random.randint(0,1) else 'Попка дурак🐔'
			else:
				continue
			vkr.send_message(
				uid=update[3],
				text=text + "'",
				rnd_id=update[7]+1
			)
			last_rnd_id = update[7]+1
response = vkr.get_new_messages()
print(response)

