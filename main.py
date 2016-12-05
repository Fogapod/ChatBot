# -*- coding: utf-8 -*-
import vklogic as vkl

import random
import requests
import time
import json
import re

__version__ = '0.0.2'
__author__ = 'Eugene Ershov - http://vk.com/fogapod'

__info__ = '''
Версия: {ver}-demo
(demo версия не мржет вестм диалог)

Я умею:
*Говорить то, что вы попросите
(/say ... |/скажи ... )
*Вызывать помощь
(/help |/помощь )
*Вести диалог
(/... )

В конце моих сообщений ставится знак верхней кавычки'

Автор: {author}'''.format(\
	ver = __version__, author = __author__
)

# qpy
import logging
logging.captureWarnings(True)

def main():
	client = vkl.Client()
	
	while not client.authorization():
		continue

	#client.save_full_message_history()
	
	last_rnd_id = 0
	url = client.make_url() # url for long polling
	print(__info__)
	print('\n{decor}{txt}{decor}'.format(decor='-'*5, txt='Listening long poll'))
	while True:
		response = requests.post(url)
		response = json.loads(response.content)
		print(response)
		url = client.make_url(keep_ts=response['ts'])
   
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
				elif re.sub('^( )*', '', text).startswith(u'/'):
					text = text[1:]
					if text.startswith(u'/'):
						text = text[1:]
						mark_msg = False
					words = text.split()
					if not text: 
						words = ' '
					if re.match(u'^((help)|(помощь)|(info)|(информация)|(инфо)|\?)',\
						words[0].lower()):
						text = __info__
					elif re.match(u'^((скажи)|(say))', words[0].lower()):
						del words[0]
						text = ' '.join(words)
					else:
						text = 'Попка молодец🐔' if random.randint(0,1) else 'Попка дурак🐔'
				else:
					continue

				client.reply(
					uid = update[3],
					text = text + "'" if mark_msg else text,
					rnd_id = update[7] + 1
				)
				last_rnd_id = update[7] + 1

if __name__ == '__main__':
	main()