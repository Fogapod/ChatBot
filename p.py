import pycurl
import json
import os
import vkrequests as vkr
import re
import asyncio

class Client:
  def __init__(self):
    self.conn = pycurl.Curl()
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

  def navigate(self, url):
    self.conn.setopt(pycurl.URL, url)
    self.conn.setopt(pycurl.WRITEFUNCTION, self.on_receive)
    self.conn.perform()
    return self.data

  def on_receive(self, data):
    data = data.decode('utf-8')
    data = json.loads(data)
    self.data = data

client = Client()
last_rnd_id = 0
client.authorize()
lpd = vkr.get_long_poll_data()
url = client.set_url(
lpd['server'],
lpd['key'],
lpd['ts']
)
while True:
  response = client.navigate(url)
  print(response)
  url = client.set_url(
    lpd['server'],
    lpd['key'],
    response['ts']
  )
  for update in response['updates']:
      if update[0] is 4 and update[7] != last_rnd_id and update[3]:
        text = update[6]
        if text.lower() == 'ершов' or text.lower() == 'женя' or text.lower() == 'жень':
          text = 'А'
        elif re.sub('^( )*', '', text).startswith('/'):
          text = text[1:]
          if re.match('^скажи ', text.lower()):
            text = re.findall('^С?с?кажи (.+)/?', text)[0]
          else:
            text = 'Попка молодец🐔'
        else:
          continue
        vkr.send_message(
          uid=update[3],
          text=text + "'",
          rnd_id=update[7]+1
        )
        last_rnd_id = update[7]+1