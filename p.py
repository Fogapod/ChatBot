import pycurl
import json
import os
import vkrequests as vkr
import re
import random
import time
from io import BytesIO

class Client:
	def __init__(self):
		self.conn = pycurl.Curl()
		self.m = pycurl.CurlMulti()
		self.STREAM_URL = 'https://{}?act={}&key={}&ts={}&wait={}&mode={}&version={}'
		self.data = None
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

	def set_url(self, server, key, ts, act='a_check', wait=30, mode=128, v=1):
		self.url = self.STREAM_URL.format(server, act, key, ts, wait, mode, v)
		return self.url

client = Client()
last_rnd_id = 0
client.authorize()
lpd = vkr.get_long_poll_data()
url = client.set_url(
lpd['server'],
lpd['key'],
lpd['ts']
)

c = pycurl.Curl()
m = pycurl.CurlMulti()
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
