#!/usr/bin/env python3

from . import array, debug, file, run

import jq, json, typing

def jload(path: file.SafeFile | str) -> typing.Any:
	"""
	Deserialize a JSON string from a file.
	"""
	tmp = None
	try:
		text = file.read(path, array = False)
		if text:
			tmp = json.loads(text)
	except Exception as ex:
		debug.debug.log_error(f"utils.jquery.jload() > {file.get_path(path)}", ex)
	return tmp

def jload_array(path: file.SafeFile | str) -> list[typing.Any]:
	"""
	Deserialize multiple JSON strings from a file, separated by newlines, and append the data to a list.
	"""
	tmp = []
	for line in file.read(path, array = True):
		try:
			if line:
				tmp.append(json.loads(line))
		except Exception as ex:
			debug.debug.log_error(f"utils.jquery.jload_array() > {file.get_path(path)}", ex)
	return tmp

def jdump(data: typing.Any):
	"""
	Serialize data to a JSON string.\n
	Returns an empty string if data is empty, for example, '[]', '{}', etc.
	"""
	tmp = ""
	try:
		if data:
			tmp = json.dumps(data, indent = 4, ensure_ascii = False)
	except Exception as ex:
		debug.debug.log_error(f"utils.jquery.jdump()", ex)
	return tmp

def find(data: typing.Any | str, query: str, sort = True, dump = False) -> typing.Any | str:
	"""
	Extract all matches from data using the specified JQ pattern.\n
	Returns a unique [sorted] list if the result is not a nested list.\n
	Dumping will serialize the result to a JSON string; returns an empty string if the result is empty, for example, '[]', '{}', etc.
	"""
	tmp = []
	try:
		if data:
			tmp = jq.compile(query).input_text(data).all() if isinstance(data, str) else jq.compile(query).input_value(data).all()
			if tmp:
				if not array.is_nested(tmp):
					tmp = array.unique(tmp, sort)
	except Exception as ex:
		debug.debug.log_error(f"utils.jquery.find() > {query}", ex)
	if dump:
		tmp = jdump(tmp)
	return tmp

def find_append_file(data: typing.Any | str, out: file.SafeFile | str, query: str, sort = True, dump = False):
	"""
	Extract all matches from data using the specified JQ pattern, append them to a file, and return the result.\n
	Returns a unique [sorted] list if the result is not a nested list.\n
	Dumping will serialize the result to a JSON string; returns an empty string if the result is empty, for example, '[]', '{}', etc.
	"""
	tmp = find(data, query, sort, dump)
	file.append(tmp, out)
	return tmp

def find_insert_file(data: typing.Any | str, out: file.SafeFile | str, query: str, sort = True, dump = False):
	"""
	Extract all matches from data using the specified JQ pattern, insert them to a file, and return the result.\n
	Returns a unique [sorted] list if the result is not a nested list.\n
	Dumping will serialize the result to a JSON string; returns an empty string if the result is empty, for example, '[]', '{}', etc.
	"""
	tmp = find(data, query, sort, dump)
	file.insert(tmp, out)
	return tmp

def results(results: list[run.Result], primary_key: str, secondary_key: str, query = "") -> list[dict[str, typing.Any | str]]:
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
