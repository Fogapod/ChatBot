# -*- coding: utf-8 -*-
import vklogic as vkl

from io import BytesIO
import random
import pycurl
import time
import json
import re

__version__ = '0.1.0'
__author__ = 'Eugene Ershov http://vk.com/fogapod'

#print(vkr.get_user_id(link=input('Короткая ссылка на страницу друга: ')))
def animate_loading(text, delay):
	loading_symbols = ('|', '/', '-', '\\')
	for i, symbol in enumerate(loading_symbols):
		print('#{} {}\r'.format(text, symbol), end='')
		time.sleep(delay/len(loading_symbols))

def main():
	client = vkl.Client()
	
	client.authorize()
	client.save_full_message_history()

	url = client.make_url()
	c = pycurl.Curl()
	m = pycurl.CurlMulti()

	last_rnd_id = 1
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
			animate_loading('Listening long poll...', 1)
			while 1:
				ret, num_handles = m.perform()
				if ret != pycurl.E_CALL_MULTI_PERFORM:
					break

		m.remove_handle(c)
		response = s.getvalue()
		response = response.decode('utf-8')
		response = json.loads(response)

		url = client.make_url(keep_ts=response['ts'])

		for update in response['updates']:
			if update[0] is 4 and update[7] != last_rnd_id and update[3]:
				text = update[6]
				mark_msg = True
				if text.lower() == 'ершов' or\
						text.lower() == 'женя' or\
						text.lower() == 'жень' or\
						text.lower() == 'женька' or\
						text.lower() == 'жека' or\
						text.lower() == 'жэка':
					text = 'А'
					mark_msg = False
				elif 'HALP' in text:
					text = 'Кому нужна помощь?!'
				elif re.sub('^( )*', '', text).startswith('/'):
					text = text[1:]
					if text.startswith('/'):
						text = text[1:]
						mark_msg = False
					words = text.split()
					if not words: 
						words = ' '
					if re.match(u'^((help)|(помощь))', words[0].lower()):
						text =\
'''Версия: {ver}
Я умею:
*Говорить то, что вы попросите
(/say text|/скажи текст)
*Вызывать помощь
(/help|/помощь)
Получить ответ без кавычки' в конце: используйте //

Автор: {author}'''.format(\
ver = __version__,
author = __author__
)

					elif re.match(u'^((скажи)|(say))', words[0].lower()):
						del words[0]
						text = ' '.join(words)
					else:
						text = 'Попка молодец🐔' if random.randint(0,1) else 'Попка дурак🐔'
				else:
					continue

				client.reply(
					uid = update[3],
					text = text + "'" if mark_mag else text,
					rnd_id = update[7] + 1
				)
				last_rnd_id = update[7] + 1

if __name__ == '__main__':
	main()
