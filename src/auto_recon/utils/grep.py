#!/usr/bin/env python3

from . import array, debug, file, run

import regex as re

FLAGS = re.MULTILINE | re.IGNORECASE

# ----------------------------------------

def find(text: str, query: str, sort = True) -> list[str]:
	"""
	Extract all matches from a text using the specified RegEx pattern.\n
	Returns a unique [sorted] list if the result is not a nested list.
	"""
	tmp = []
	try:
		if text:
			tmp = re.findall(query, text, flags = FLAGS)
			if tmp:
				if not array.is_nested(tmp):
					tmp = array.unique(tmp, sort)
	except Exception as ex:
		debug.debug.log_error(f"utils.grep.find() > {query}", ex)
	return tmp

def find_append_file(text: str, out: file.SafeFile | str, query: str, sort = True):
	"""
	Extract all matches from a text using the specified RegEx pattern, append them to a file, and return the result.\n
	Returns a unique [sorted] list if the result is not a nested list.
	"""
	tmp = find(text, query, sort)
	file.append(tmp, out)
	return tmp

def find_insert_file(text: str, out: file.SafeFile | str, query: str, sort = True):
	"""
	Extract all matches from a text using the specified RegEx pattern, insert them to a file, and return the result.\n
	Returns a unique [sorted] list if the result is not a nested list.
	"""
	tmp = find(text, query, sort)
	file.insert(tmp, out)
	return tmp

def search(text: str, query: str):
	"""
	Check if there are any matches in a text using the specified RegEx pattern.
	"""
	success = False
	try:
		if text:
			if re.search(query, text, flags = FLAGS):
				success = True
	except Exception as ex:
		debug.debug.log_error(f"utils.grep.search() > {query}", ex)
	return success

def replace(text: str, query: str, new = "", count = 0):
	"""
	Replace all matches from a text using the specified RegEx pattern with a new value.
	"""
	try:
		if text:
			text = re.sub(query, new, text, flags = FLAGS, count = count)
	except Exception as ex:
		debug.debug.log_error(f"utils.grep.replace() > {query}", ex)
	return text

def results(results: list[run.Result], primary_key: str, secondary_key: str, query = "") -> list[dict[str, list[str] | str]]:
	"""
	Parse results.\n
	The primary key stores 'result.data', while the secondary key stores 'result.response'.\n
	The query applies only to 'result.response'.
	"""
	tmp = []
	for result in results:
		if result.response:
			if query:
				result.response = find(result.response, query)
			if result.response:
				tmp.append({
					primary_key: result.data,
					secondary_key: result.response
				})
	return tmp
