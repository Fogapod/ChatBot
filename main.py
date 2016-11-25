# -*- coding: utf-8 -*-
import vkrequests as vkr
import os.path

login = input('Логин: ')
password = input('Пароль: ')

if os.path.exists('data/token.txt'):
	token = open('data/token.txt', 'r').read()
	if vkr.log_in(token=token):
		print(u'Успешная авторизация')
	else:
		print(u'Авторизация не удалась')
else:
	token = vkr.log_in(login=login, password=password)
	if token:
		print(u'Успешная авторизация')
		open('data/token.txt', 'w').write(token)
	else:
		print(u'Авторизация не удалась')

with open('data/message_dump.txt', 'w') as f:
	pass