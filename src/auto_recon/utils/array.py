#!/usr/bin/env python3

def is_nested(array: list):
	"""
	Returns 'True' if 'array' contains a list, dictionary, or tuple.\n
	For example, '[[...]]', '[{...}]', '[(...)]', etc.
	"""
	return any(isinstance(entry, (list, dict, tuple)) for entry in array)

def remove_empty_strings(array: list[str]) -> list[str]:
	"""
	Strip whitespace from each string in 'array', and remove empty strings.
	"""
	tmp = []
	for entry in array:
		entry = entry.strip()
		if entry:
			tmp.append(entry)
	return tmp

def to_lowercase(array: list[str]):
	"""
	Convert all strings in 'array' to lowercase.
	"""
	return [entry.lower() for entry in array]

def unique(array: list[str], sort = True):
	"""
	Unique sort all strings in 'array' in descending order.\n
	Primarily, to ensure that HTTPS URLs appear at the top of the list.
	"""
	seen = set()
	array = [x for x in array if not (x in seen or seen.add(x))]
	if sort and array:
		array = sorted(array, key = str.casefold, reverse = True)
	return array

def join(array: list) -> str:
	"""
	Join 'array' using a single space as the separator.\n
	Each element in 'array' will be cast to a string, stripped of whitespace, and removed if empty.
	"""
	tmp = []
	for entry in array:
		entry = str(entry).strip()
		if entry:
			tmp.append(entry)
	return (" ").join(tmp)

def filter_blacklist(array: list[str], keywords: list[str], case_sensitive = False, sort = True):
	"""
	Remove all strings from 'array' that contain a blacklisted keyword.\n
	Returns a unique [sorted] list.
	"""
	tmp = []
	if case_sensitive:
		for entry in array:
			if any(keyword in entry for keyword in keywords):
				continue
			tmp.append(entry)
	else:
		keywords = to_lowercase(keywords)
		for entry in array:
			if any(keyword in entry.lower() for keyword in keywords):
				continue
			tmp.append(entry)
	return unique(tmp, sort)

def filter_whitelist(array: list[str], keywords: list[str], case_sensitive = False, sort = True):
	"""
	Remove all strings from 'array' that do not contain a whitelisted keyword.\n
	Returns a unique [sorted] list.
	"""
	tmp = []
	if case_sensitive:
		for entry in array:
			if not any(keyword in entry for keyword in keywords):
				continue
			tmp.append(entry)
	else:
		keywords = to_lowercase(keywords)
		for entry in array:
			if not any(keyword in entry.lower() for keyword in keywords):
				continue
			tmp.append(entry)
	return unique(tmp, sort)
