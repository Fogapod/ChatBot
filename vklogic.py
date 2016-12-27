# -*- coding: utf-8 -*-
import vkrequests as vkr
from utils import parse_input
from utils import parse_chat_dump
from utils import get_sticker_meaning

import os
import time

p = '/storage/emulated/0/'

class Profiler():
	def __enter__(self):
		self._startTime = time.time()

	def __exit__(self, type, value, traceback):
		print('Время выполнения: {:.3f} с.'.format(time.time() - self._startTime))

class Client:
	def __init__(self):
		self.SELF_ID = None # user_id ( vk.com/... )
		self.lpd = None # LongPollData

	def authorization(self):
		try:
			with open(p+'Git/ChatBot/data/token.txt', 'r') as token_file:
				token = token_file.readlines()[0][:-1]
		except IOError:
			token = None

		if token:
			if vkr.log_in(token=token):
				self.SELF_ID = vkr.get_user_id()
				return True
			else:
				return False

		else:
			login, password = self._get_login_and_password()
			new_token = vkr.log_in(login=login, password=password)
			if new_token:
				with open(p+'Git/ChatBot/data/token.txt', 'w') as token_file:
					token_file.write('{}\n{}'.format(\
						new_token, 'НИКОМУ НЕ ПОКАЗЫВАЙТЕ СОДЕРЖИМОЕ ЭТОГО ФАЙЛА'
						)
					)
				self.SELF_ID = vkr.get_user_id()
				return True
			else:
				return False


	def _get_login_and_password(self):
		login = raw_input('Логин: ')
		password = raw_input('Пароль: ')
		return login, password

	def save_full_message_history(self):
		if os.path.exists(p+'Git/ChatBot/data/message_dump.txt'):
			while True:
				ans = raw_input('Файл с историей сообщений уже существует. Заменить его? (y/n) ')
				if ans.lower() == 'y' or ans == '':
					with Profiler():
						with open(p+'Git/ChatBot/data/message_dump.txt', 'a+') as f:
							f.seek(0)
							f.truncate()
							self.message_getter(f)
						parse_chat_dump(p+'Git/ChatBot/data/message_dump.txt', p+'Git/ChatBot/data/message_dump.txt')
						break
				elif ans.lower() == 'n':
					break
				else:
					print('Неизвестный ответ.')
		else:
			with Profiler():
				with open(p+'Git/ChatBot/data/message_dump.txt', 'a+') as f:
					f.seek(0)
					f.truncate()
					self.message_getter(f)
				parse_chat_dump(p+'Git/ChatBot/data/message_dump.txt', p+'Git/ChatBot/data/message_dump.txt')


	def message_getter(self, file):
		#TODO: распознование стикеров
		messages_list = vkr.get_messages_list()
		print('Обнаружено {} диалогов'.format(messages_list['count']))
		for k in range(messages_list['count']//200 + 1):

			for d in range(len(messages_list['items'])):
				msg_list = messages_list['items'][d]
				messages = vkr.get_messages(
					uid=msg_list['message']['user_id']
				)
				time.sleep(0.33)

				if 'chat_id' in msg_list['message']:
					print('Сообщения из беседы, пропускаю')
					continue
				else:
					uname = vkr.get_user_name(
								uid=msg_list['message']['user_id']
								)
					print('Сообщений в диалоге: {}::{}'.format(\
							messages['count'], uname
								)
							)
					file.write('### {}::{}\n'.format(uname, msg_list['message']['user_id']))

				for i in range(messages['count']//200 + 1):
					for j in range(len(messages['items'])):
						msg = messages['items'][j]
						text = msg['body']
						if text != '':
							text = parse_input(text) 
							file.write(
							'{} {}\n'.format(\
								'<A>' if msg['from_id'] == self.SELF_ID else '<Q>',
								text
								)
							)
						elif 'attachments' in msg and msg['attachments'][0]['type'] == 'sticker':
						    text = get_sticker_meaning(msg['attachments'][0]['sticker'])
						    file.write(
						    '{} {}\n'.format(\
							    '<A>' if msg['from_id'] == self.SELF_ID else '<Q>',
							    text
							    )
						    )
							
					print('Iteration {}.{}'.format(i+1, len(messages['items'])))
					messages = vkr.get_messages(
						offset=(i+1)*200, uid=msg_list['message']['user_id']
					)
					time.sleep(0.33)
				file.write('### {}::{}\n\n'.format(uname, msg_list['message']['user_id']))
				print('Завершена обработка диалога №{}/{}'.format(k*200+d+1, messages_list['count']))
			messages_list = vkr.get_messages_list(offset=(k+1)*200)

	def flood(self, chat_id):
		while True:
			ans = raw_input('Начать флуд в {}? (Y/N) '.format(chat_id)) 
			if ans.upper() == 'Y':
				print('Начинаю флудить...')
				for i in range(1000):
					vkr.send_message(text=str(i+1),uid=chat_id,rnd_id=i)
					time.sleep(2)
			elif ans.upper() == 'N':
				break
			else:
				print('Ответ не распознан, повторите')

	def make_url(self, keep_ts=False):
		# long poll request url
		if keep_ts:
			self.lpd['ts'] = keep_ts
		else: 
			self.lpd = vkr.get_long_poll_data()

		if self.lpd:
			url_pattern = 'https://{server}?act={act}&key={key}&ts={ts}&wait={w}&mode={m}&version={v}'
			url = url_pattern.format(
				server = self.lpd['server'],
				key = self.lpd['key'],
				ts = self.lpd['ts'],
				act = 'a_check',
				w = 100,
				m = 128,
				v = 1
			)
			return url