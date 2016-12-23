# -*- coding: utf-8 -*-
#qpy:2
import vklogic as vkl
from utils import parse_input

from threading import Thread
import random
import requests
import time
import json
import re

__version__ = '0.0.4'
__author__ = 'Eugene Ershov - http://vk.com/fogapod'
__source__ = 'https://github.com/Fogapod/ChatBot/'
	
__info__ = '''
Версия: {ver}-demo
(demo версия не может вестм диалог)

Я умею:
*Говорить то, что вы попросите
(/say ... |/скажи ... )
*Вызывать помощь
(/help |/помощь )
*Вести диалог
(/... )

В конце моих сообщений ставится знак верхней кавычки'

Автор: {author}
Мой исходный код: {source}
'''.format(\
	ver = __version__, author = __author__, source = __source__
)

# qpy
import logging
logging.captureWarnings(True)
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
p = '/storage/emulated/0/'
# qpy

client = vkl.Client()
	
while not client.authorization():
	continue

client.save_full_message_history()
	
url = client.make_url() # url for long polling
	
long_poll_response = None

def listen_long_poll():
	global long_poll_response
	global url

	print('{decor}{txt}{decor}'.format(decor='-'*6, txt='Listening long poll'))

	while True:
		if not long_poll_response:
			long_poll_response = requests.post(url)
		else:
			continue # прошлый запрос не обработан

long_poll_process = Thread(target=listen_long_poll)

def main():
	print(__info__)

	global long_poll_response
	global url
	
	long_poll_process.start()
	last_rnd_id = 0
	while True:
		if not long_poll_response:
			time.sleep(0.1)
			continue

		response = json.loads(long_poll_response.content)
		url = client.make_url(keep_ts=response['ts'])
		long_poll_response = None
		print(response)
   
		for update in response['updates']:
			if update[0] == 4 and\
					update[7] != last_rnd_id and\
					update[6] != '':
			# response == message
			# message != last_message
			# message != ''
				text = update[6]
				mark_msg = True
				if text.lower() == u'ершов' or\
						text.lower() == u'женя' or\
						text.lower() == u'жень' or\
						text.lower() == u'женька' or\
						text.lower() == u'жека' or\
						text.lower() == u'жэка':
					text = 'А'
					mark_msg = False

				elif 'HALP' in text:
					text = 'Кому нужна помощь?!'

				elif re.sub('^( )*', '', text).startswith('/'):	

					if text.startswith('/'):
						mark_msg = False
						text = text[1:]

					text = parse_input(text, replace_vkurl=False, replace_nl=False)
					words = text.split()

					if not words: 
						words = ' '

					if re.match(u'^((help)|(помощь)|(info)|(инфо)|(информация)|\?)',\
							words[0].lower()):
						text = __info__
					elif re.match(u'^((скажи)|(say))', words[0].lower()):
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
