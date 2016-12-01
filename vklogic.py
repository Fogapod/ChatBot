# -*- coding: utf-8 -*-
import vkrequests as vkr

import os

#print(vkr.get_user_id(link=input('Короткая ссылка на страницу друга: ')))

class Client:
	def __init__(self):
		self.SELF_ID = None
		self.lpd = None

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

	def save_full_message_history(self):
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

	def reply(self, **kwargs):
		vkr.send_message(
			uid = kwargs.get('uid'),
			text = kwargs.get('text'),
			rnd_id = kwargs.get('rnd_id')
		)

	def make_url(self, keep_ts=False):
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