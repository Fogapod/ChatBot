# -*- coding: utf-8 -*-
import re
def parse_input(string, replace_vkurl=True, replace_url=True, replace_nl=True):
	new_string = string

	if replace_vkurl:
		new_string = re.sub(r'(https?://)?m|\.?vk\.com/?.*',
			'__vkurl__',
			new_string.lower() # поиск ссылок vk.com
		)

	if replace_url:
		new_string = re.sub(
		r'''(?i)\b((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/?)(?:[^\s()<>]+|(([^\s()<>]+|(([^\s()<>]+)))*))+(?:(([^\s()<>]+|(([^\s()<>]+)))*)|[^\s`!()[]{};:'".,<>?«»“”‘’]))'''
		, '__url__', # поиск всех остальных ссылок
		new_string
	)

