# -*- coding: utf-8 -*-
import vkrequests as vkr
import os.path

def authorize():
	if os.path.exists('data/token.txt'):
		token = open('data/token.txt', 'r').read()

		if vkr.log_in(token=token):
			print(u'Успешная авторизация')
		else:
			print(u'Авторизация не удалась')

	else:
		login = input('Логин: ')
		password = input('Пароль: ')
		token = vkr.log_in(login=login, password=password)

		if token:
			print(u'Успешная авторизация')
			open('data/token.txt', 'w').write(token)
		else:
			print(u'Авторизация не удалась')

authorize()

with open('data/message_dump.txt', 'w') as f:
	pass