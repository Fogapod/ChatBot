# -*- coding: utf-8 -*-
import vklogic as vkl

import random
import requests
import time
import json
import re

__version__ = '0.1.0'
__author__ = 'Eugene Ershov http://vk.com/fogapod'

__info__ =\
'''
Версия: {ver}
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

# qpy
import sys
reload(sys)
#sys.setdefaultencoding('utf-8')
import logging
logging.captureWarnings(True)

def main():
	client = vkl.Client()
	
	client.authorize()
	#client.save_full_message_history()

	url = client.make_url()

	last_rnd_id = 1
	print(__info__)
	print('\n{dec}{txt}{dec}'.format(dec='-'*5, txt='Listening long poll'))
	while True:
		response = requests.post(url)
		response = json.loads(response.content)
		print(response)
		url = client.make_url(keep_ts=response['ts'])

		for update in response['updates']:
			if update[0] is 4 and update[7] != last_rnd_id and update[3]:
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