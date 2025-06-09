#!/usr/bin/env python3

from . import array, config, debug

import dataclasses, os, threading

ENCODING = "ISO-8859-1"

# ----------------------------------------

@dataclasses.dataclass
class SafeFile:
	"""
	Initialize a thread-safe file.
	"""
	path: str
	lock: threading.Lock = threading.Lock()

def get_path(file: SafeFile | str):
	"""
	If 'file' is an instance of 'SafeFile' class, return 'file.path'; otherwise, return 'file'.
	"""
	return file.path if isinstance(file, SafeFile) else file

# ----------------------------------------

def validate(file: str):
	"""
	Validate a file.\n
	Success flag is 'True' if 'file' exists, is a regular file, has a read permission, and is not empty.
	"""
	success = False
	message = ""
	if not os.path.isfile(file):
		message = f'"{file}" does not exist'
	elif not os.access(file, os.R_OK):
		message = f'"{file}" does not have a read permission'
	elif not os.stat(file).st_size > 0:
		message = f'"{file}" is empty'
	else:
		success = True
	return success, message

def validate_silent(file: str):
	"""
	Silently validate a file.\n
	Returns 'True' if 'file' exists, is a regular file, has a read permission, and is not empty.
	"""
	success, ignored = validate(file)
	return success

def remove(file: str):
	"""
	Remove a file.
	"""
	success = True
	message = ""
	try:
		if os.path.exists(file):
			os.remove(file)
	except Exception:
		success = False
		message = f'Cannot remove "{file}"'
	return success, message

def remove_silent(file: str):
	"""
	Silently remove a file.
	"""
	success, ignored = remove(file)
	return success

def __read(file: str):
	"""
	Silently validate and read a file as text.\n
	Whitespace will be stripped from the text.
	"""
	tmp = ""
	try:
		if validate_silent(file):
			tmp = open(file, "r", encoding = ENCODING).read().strip()
	except Exception as ex:
		debug.debug.log_error(f"utils.file.__read() > {file}", ex)
	return tmp

def __read_array(file: str) -> list[str]:
	"""
	Silently validate and read a file line by line, and append the lines to a list.\n
	Whitespace will be stripped from each line, and empty lines removed.
	"""
	tmp = []
	try:
		if validate_silent(file):
			with open(file, "r", encoding = ENCODING) as stream:
				for line in stream:
					line = line.strip()
					if line:
						tmp.append(line)
	except Exception as ex:
		debug.debug.log_error(f"utils.file.__read_array() > {file}", ex)
	return tmp

def read(file: SafeFile | str, array = True):
	"""
	Silently validate and read a file as text or line by line, and append the lines to a list.\n
	Whitespace will be stripped from the text, or, if 'array' is set to 'True', from each line, and empty lines will be removed.
	"""
	if isinstance(file, SafeFile):
		with file.lock:
			return __read_array(file.path) if array else __read(file.path)
	else:
		return __read_array(file) if array else __read(file)

def __write(text: str, out: str, flags = "w"):
	"""
	Write a text to an output file.\n
	Whitespace will be stripped from the text.\n
	If the text is empty, nothing will be written.
	"""
	try:
		text = text.strip()
		if text:
			open(out, flags, encoding = ENCODING).write(f"{text}\n")
	except Exception as ex:
		debug.debug.log_error(f"utils.file.__write() > {out}", ex)

def __write_array(text_array: list[str], out: str, flags = "w"):
	"""
	Write a text array to an output file.\n
	Whitespace will be stripped from each string in the text array, and empty strings will be removed.\n
	If the text array is empty, nothing will be written.
	"""
	try:
		text_array = array.remove_empty_strings(text_array)
		if text_array:
			with open(out, flags, encoding = ENCODING) as stream:
				for entry in text_array:
					stream.write(f"{entry}\n")
	except Exception as ex:
		debug.debug.log_error(f"utils.file.__write_array() > {out}", ex)

def write(data: list[str] | str, out: SafeFile | str, flags = "w"):
	"""
	Write data to an output file.\n
	Whitespace will be stripped from data, or if data is a list, from each string in the list, and empty strings will be removed.\n
	If data is empty, nothing will be written.
	"""
	if isinstance(out, SafeFile):
		with out.lock:
			__write_array(data, out.path, flags) if isinstance(data, list) else __write(data, out.path, flags)
	else:
		__write_array(data, out, flags) if isinstance(data, list) else __write(data, out, flags)

def append(data: list[str] | str, out: SafeFile | str):
	"""
	Append data to an output file.\n
	Whitespace will be stripped from data, or if data is a list, from each string in the list, and empty strings will be removed.\n
	If data is empty, nothing will be written.
	"""
	write(data, out, "a")

def insert(data: list[str] | str, out: SafeFile | str):
	"""
	Insert data to an output file.\n
	Whitespace will be stripped from data, or if data is a list, from each string in the list, and empty strings will be removed.\n
	If data is empty, nothing will be written.
	"""
	write(data, out, "w")

def copy_append(source: SafeFile | str, destination: SafeFile | str, array = True):
	"""
	Copy the content of the source, append it to the destination, and return the appended content.\n
	Whitespace will be stripped from the content, or if content is a list, from each string in the list, and empty strings will be removed.\n
	If the content is empty, nothing will be written.\n
	'array' applies only when reading the source.
	"""
	tmp = read(source, array)
	append(tmp, destination)
	return tmp

def copy_insert(source: SafeFile | str, destination: SafeFile | str, array = True):
	"""
	Copy the content of the source, insert it to the destination, and return the inserted content.\n
	Whitespace will be stripped from the content, or if content is a list, from each string in the list, and empty strings will be removed.\n
	If the content is empty, nothing will be written.\n
	'array' applies only when reading the source.
	"""
	tmp = read(source, array)
	insert(tmp, destination)
	return tmp

# ----------------------------------------

class File:

	def __init__(self):
		"""
		Initialize a class for managing files.
		"""
		self.initialize("")

	def initialize(self, root_directory: str):
		"""
		[Re]initialize.
		"""
		self.__root_directory: str = root_directory
		self.__files: dict[config.TXT | config.JSON, SafeFile] = {}
		for key in config.TXT:
			self.__files[key] = self.__init_safe_file(f"{key.value}.txt")
		for key in config.JSON:
			self.__files[key] = self.__init_safe_file(f"{key.value}.json")

	def __init_safe_file(self, filename: str):
		"""
		Initialize a thread-safe file in the root directory.
		"""
		return SafeFile(os.path.join(self.__root_directory, filename))

	def get(self, key: config.TXT | config.JSON) -> SafeFile:
		"""
		Get the thread-safe class object to a file for the specified key.\n
		Returns 'None' if the specified key does not exist.
		"""
		file = None
		try:
			file = self.__files[key]
		except Exception as ex:
			debug.debug.log_error(f"utils.file.File().get() > {key}", ex)
		return file

file = File()
"""
Singleton class instance for managing files.
"""
