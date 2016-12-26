# -*- coding: utf-8 -*-
import vklogic as vkl
import vkrequests as vkr
from utils import parse_input

from threading import Thread
import random
import requests
import time
import json
import re
import math

__version__ = '0.0.5'
__author__ = 'Eugene Ershov - https://vk.com/fogapod'
__source__ = 'https://github.com/Fogapod/ChatBot/tree/qpy2.7'
	
__info__ = '''
Версия: {ver}-demo
(demo версия не может вести диалог)

Я умею:
*Говорить то, что вы попросите
(/say ... |/скажи ... )
*Производить математические операции
(/calculate ... |/посчитай ... )
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

class LongPollSession(object):
    def __init__(self, client):
        self.client = client
        self.mlpd = mlpd = None # message_long_poll_data
        #{
        #   server: str,
        #   key: int,
        #   ts: int
        #}
        self.last_rnd_id = 0
        self.reply_count = 0
        self.message_long_poll_url = self._make_message_long_poll_url()
        self.run_message_long_poll_process = True
        self.message_long_poll_process = Thread(target=self._listen_message_long_poll)
        self.message_long_poll_response = None
        self.SELF_ID = vkr.get_self_id()
        self.exiting_text = 'Завершаю программу'

    def __exit__(self):
        self.run_message_long_poll_process = False
        self.message_long_poll_response = []
        exit()
        
    def _make_message_long_poll_url(self, keep_ts=False):
        """
        :keep_ts:
            использовать значение ts, полученное в результате события {ts: 12345, updates: []} (предполагается, что все поля mlpd заполнены)
        Возвращает: готовый url для осуществления long poll запроса
        """
        if keep_ts:
            self.mlpd['ts'] = keep_ts
        else: 
            self.mlpd = vkr.get_message_long_poll_data()

        if self.mlpd:
            url_pattern = 'https://{server}?act={act}&key={key}&ts={ts}&wait={w}&mode={m}&version={v}'
            url = url_pattern.format(
                server = self.mlpd['server'],
                key = self.mlpd['key'],
                ts = self.mlpd['ts'],
                act = 'a_check',
                w = 100,
                m = 130,
                v = 1
            )
            return url


    def _listen_message_long_poll(self):
        """
        Позволяет получать новые события (нужно запускать отдельным потоком)
        При получении события меняет значение переменной message_long_poll_response с None на ответ сервера
        """
        print('{decor}{txt}{decor}'.format(decor='-'*6, txt='Listening long poll'))

        while self.run_message_long_poll_process:
            if not self.message_long_poll_response:
                self.message_long_poll_response = vkr.do_message_long_poll_request(url=self.message_long_poll_url)
            else:
                # прошлый ответ ещё не обработан
                time.sleep(0.01)

    def process_updates(self):
        print (__info__)
        self.message_long_poll_process.start()
        while True:
            if not self.message_long_poll_response:
                time.sleep(0.1)
                continue

            response = json.loads(self.message_long_poll_response.content)
            self.message_long_poll_url = self._make_message_long_poll_url(keep_ts=response['ts'])
            self.message_long_poll_response = None

            print(response)

            for update in response['updates']:
                if  update[0] == 4 and\
                    update[8] != self.last_rnd_id and\
                    update[6] != '':
                # response == message
                # message != last_message
                # message != ''
                    text = update[6]
                    mark_msg = True
                else:
                    continue

                if  text.lower() == 'ершов' or\
                    text.lower() == 'женя' or\
                    text.lower() == 'жень' or\
                    text.lower() == 'женька' or\
                    text.lower() == 'жека' or\
                    text.lower() == 'евгений' or\
                    text.lower() == 'ерш' or\
                    text.lower() == 'евгеха' or\
                    text.lower() == 'жэка':
                    text = 'А'

                elif text.lower() == 'how to praise the sun?' or\
                     text.lower() == '🌞':
                    text = '\\[T]/\n..🌞\n...||\n'

                elif re.sub('^( )*', '', text).startswith('/'):	
                    text = text[1:]
                    if text.startswith('/'):
                        mark_msg = False
                        text = text[1:]

                    text = parse_input(text, replace_vkurl=False, replace_nl=False)
                    words = text.split()

                    if not words: 
                        words = ' '

                    if  re.match(u'^((help)|(помощь)|(info)|(инфо)|(информация)|\?)',\
                        words[0].lower()):
                        text = __info__
						
                    elif re.match(u'^((скажи)|(say))', words[0].lower()):
                        del words[0]
                        text = ''.join(words)
						
                    elif re.match(u'^((посчитай)|(calculate))', words[0].lower()):
                        del words[0]
                        words = ''.join(words).lower()
                        if not re.match(u'[^\d+\-*/:().,^√πe]', words) or re.match('(sqrt\(\d+\))|(pi)', words):
                            words = ' ' + words + ' '
                            words = re.sub(',', '.', words)
                            words = re.sub(':', '/', words)
                            while True:
                                index = re.search('[^.\d]\d+[^.\de]', words)
                                if index:
                                    index = index.end() - 1
                                    words = words[:index] + '.' + words[index:]
                                else:
                                    break
                            words = re.sub(u'(sqrt)|√', 'math.sqrt', words)
                            words = re.sub(u'(pi)|π', 'math.pi', words)
                            words = re.sub('\^', '**', words)
                            print words
                            try:
                                text = str(eval(words))
                            except SyntaxError:
                                text = 'Ошибка [0]'
                            except NameError:
                                text = 'Ошибка [1]'
                            except AttributeError:
                                text = 'Ошибка [2]'        
                            except ZeroDivisionError:
                                text = 'Деление на 0'
                            except OverflowError:
                                text = 'Слишком большой результат'
                        else:
                            text = 'Не математическая операция'
                    
                    elif re.match('stop', text.lower()):
                        if update[2] == 1 or int(update[7]['from']) == self.SELF_ID:
                            text = self.exiting_text
                        else:
                            text = 'Доступ к команде ограничен'
                    
                    else:
                        text = 'Попка молодец🐔' if random.randint(0,1) else 'Попка дурак🐔'
                        text = 'Попка умеет считать лучше тебя 🐔' if random.randint(0,1) and random.randint(0,1) and  random.randint(0,1) else text

                else:
                    continue
				
                if update[5] != ' ... ':
                    resend_message = update[1]
                else:
                    resend_message = None

                self.last_rnd_id = update[8] + 3
                self.client.reply(
                    uid = update[3],
                    text = text + "'" if mark_msg else text,
                    forward = resend_message,
                    rnd_id = self.last_rnd_id
                    )
                self.reply_count += 1
                if text == self.exiting_text:
                    self.__exit__()

def main():
    client = vkl.Client()
	
    while not client.authorization():
        continue

    client.save_full_message_history()
    
    session = LongPollSession(client=client)
    session.process_updates()

if __name__ == '__main__':
    main()
