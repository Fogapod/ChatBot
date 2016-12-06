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

def parse_chat_dump(path, new_path=None):
	new_lines = []
	new_line = ''
	last_line = '<A> '
	dialog_started = False
	was_new_message = False
	print('Parsing chat history, do not close the program...')
	with open(path, 'r') as file:
		lines = file.readlines()
		for line in lines:
			if line.startswith('###'):
				dialog_started = not dialog_started
				if dialog_started:
				  last_line = '<A> '
			elif line == '\n':
				continue
			elif line[:4] == last_line[:4]: # "<Q> " and "<A> "
				new_lines.append(line[4:-1] + ' __nm__ ')
				was_new_message = True
				last_line = line
			else:
				if was_new_message:
					new_line += '\n'
					was_new_message = False

				new_line +=  line[4:]
				new_lines.append(new_line)
				last_line = line
				new_line = ''

	with open('{}'.format(new_path if new_path else path), 'w') as new_file:
		for line in new_lines:
			new_file.write(line)