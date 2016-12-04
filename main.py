# -*- coding: utf-8 -*-
import vklogic as vkl

from io import BytesIO
import random
import pycurl
import time
import json
import re

__version__ = '0.1.0'
__author__ = 'Eugene Ershov - http://vk.com/fogapod'

__info__ = '''
Версия: {ver}
Я умею:
*Говорить то, что вы попросите
(/say text|/скажи текст)
*Вызывать помощь
(/help|/помощь)

Автор: {author}'''.format(\
	ver = __version__, author = __author__
)

def animate_loading(text, delay):
	loading_symbols = ('|', '/', '-', '\\')
	for i, symbol in enumerate(loading_symbols):
		print('#{} {}\r'.format(text, symbol), end='')
		time.sleep(delay/len(loading_symbols))

def main():
	client = vkl.Client()
	
	while not client.authorization():
		continue

	client.save_full_message_history()

	url = client.make_url()
	c = pycurl.Curl()
	m = pycurl.CurlMulti()

	last_rnd_id = 1
	reply_count = 0
	while True:
		s = BytesIO()
		c.setopt(c.URL, url)
		c.setopt(c.WRITEFUNCTION, s.write)
		m.add_handle(c)

		while True:
			ret, num_handles = m.perform()
			if ret != pycurl.E_CALL_MULTI_PERFORM:
				break

		while num_handles: # main loop
			animate_loading(
				'Listening long poll... {} replyes'.format(reply_count), 1
				)
			while 1: # main loop (2)
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
					words = text.split()
					if not words: 
						words = ' '

					if words[0].startswith('/'):
						words[0] = words[0][1:]
						mark_msg = False

					if re.match('^((help)|(помощь)|(info)|(инфо)|(информация)|\?)',\
							words[0].lower()):
						text = __info__
					elif re.match('^((скажи)|(say))', words[0].lower()):
						del words[0]
						text = ' '.join(words)
					else:
						text = 'Попка молодец🐔' if random.randint(0,1) else 'Попка дурак🐔'

				else:
					continue

				last_rnd_id = update[7] + 1
				client.reply(
					uid = update[3],
					text = text + "'" if mark_msg else text,
					rnd_id = last_rnd_id
				)
				reply_count += 1

if __name__ == '__main__':
	main()