# -*- coding: utf-8 -*-
import re
import json
import webbrowser

p = '/storage/emulated/0/'

def parse_input(string, replace_vkurl=True, replace_url=True, replace_nl=True):
	new_string = string

	if replace_vkurl:
		new_string = re.sub(r'\b(https?://)?m\.?vk\.com/?.*\b',
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

def get_sticker_meaning(new_sticker):
	try:
		with open(p+'Git/ChatBot/data/meanings_of_stiсkers.txt', 'r') as f:
			text = re.sub("'", '"', f.read())
			stickers = json.loads(text)
	except IOError:
		with open(p+'Git/ChatBot/data/meanings_of_stiсkers.txt', 'w') as f:
			pass
		f = '{"product_id":{"0":{"id":{"0":{"photo_64":"0","meaning":"0"}}}}}'
		stickers = json.loads(f)

	if str(new_sticker['product_id']) not in stickers['product_id']:
		stickers['product_id'].update({str(new_sticker['product_id']):{'id':{}}})

	if str(new_sticker['id']) not in stickers['product_id'][str(new_sticker['product_id'])]['id']:
		stickers['product_id'][str(new_sticker['product_id'])]['id'].update({str(new_sticker['id']):{'meaning':'__sticker__','photo_64':new_sticker['photo_64']}})

	if stickers['product_id'][str(new_sticker['product_id'])]['id'][str(new_sticker['id'])]['meaning'] == '__sticker__':
		print('Ссылка на стикер: {}'.format(new_sticker['photo_64']))
		webbrowser.open_new(new_sticker['photo_64'])
		meaning = unicode(raw_input('Попробуйте определить, что он значает короткой фразой: '))

		if meaning == '':
			meaning = '__sticker__'

		stickers['product_id'][str(new_sticker['product_id'])]['id'][str(new_sticker['id'])]['meaning'] = meaning

		with open(p+'Git/ChatBot/data/meanings_of_stiсkers.txt', 'w') as f:
			f.write(str(stickers))

		return '__sticker__ ' + meaning

	else:
		return stickers['product_id'][str(new_sticker['product_id'])]['id'][str(new_sticker['id'])]['meaning']

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
				  was_new_message = False
				continue

			elif line == '\n':
				continue

			elif line[:4] == last_line[:4]: # "<Q> " and "<A> "
				new_lines.append(line[4:-1] + ' __nm__ ')
				was_new_message = True
				last_line = line
				continue

			if was_new_message:
				new_lines[len(new_lines)-1] = new_lines[len(new_lines)-1][:-len(' __nm__ ')] + '\n'
				was_new_message = False

			new_line +=  line[4:]
			new_lines.append(new_line)
			last_line = line
			new_line = ''

	with open('{}'.format(new_path if new_path else path), 'w') as new_file:
		for line in new_lines:
			new_file.write(line)