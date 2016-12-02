# -*- coding: utf-8 -*-
import vklogic as vkl

import random
import requests
import time
import json
import re

# qpy
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import logging
logging.captureWarnings(True)

p = '/storage/emulated/0/Git/ChatBot/'
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

	last_rnd_id = 1
	while True:
		response = requests.post(url)
		response = json.loads(response.content)

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
'''Версия: 0.1
Я умею:
	Говорить то, что вы попросите (/say text|/скажи текст)
	Вызывать помощь (/help|/помощь)
Получить ответ без кавычки' в конце: используйте //'''

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