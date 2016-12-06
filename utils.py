# -*- coding: utf-8 -*-
import re
def parse_input(string, replace_vkurl=True, replace_url=True, replace_nl=True):
	new_string = string

	if replace_vkurl:
		new_string = re.sub(r'(https?://)?m\.?vk\.com/?.*',
			'__vkurl__',
			new_string # поиск ссылок vk.com
		)

	if replace_url:
		new_string = re.sub(
		r'''(?i)\b((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/?)(?:[^\s()<>]+|(([^\s()<>]+|(([^\s()<>]+)))*))+(?:(([^\s()<>]+|(([^\s()<>]+)))*)|[^\s`!()[]{};:'".,<>?«»“”‘’]))'''
		, '__url__', # поиск всех остальных ссылок
		new_string
	)

	if replace_nl:
		new_string = re.sub('\n', ' __nl__ ', new_string) # поиск переносов на новую строку

	return new_string

def parse_chat_dump(path):
	new_lines = []
	last_line = '<A> '
	print('Parsing chat history, do not close the program...')
	with open(path, 'r+') as file:
		lines = file.readlines()
		for line in lines:
			if line.startswith('###') or line == '' or line == '\n':
				continue
			elif line[:4] == last_line[:4]:
				continue
			else:
				new_lines.append(line[4:])
				last_line = line

		file.seek(0)
		file.truncate()
		for line in new_lines:
			file.write(line)
