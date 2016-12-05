# -*- coding: utf-8 -*-
import re
def parse_input(string):
	re.sub(r'(https?://)?(m\.)?vk\.com/.*$',
		'__vkurl__',
		string.lower() # поиск ссылок vk.com
	)

	string = re.sub(
		r'''(?i)\b((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|(([^\s()<>]+|(([^\s()<>]+)))*))+(?:(([^\s()<>]+|(([^\s()<>]+)))*)|[^\s`!()[]{};:'".,<>?«»“”‘’]))'''
		, '__url__', # поиск всех остальных ссылок
		string
	)

	string = re.sub('\n', '__nl__', string) # поиск переносов на новую строку
	return string