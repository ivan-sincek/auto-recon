#!/usr/bin/env python3

from . import config, debug, file

import os, shutil

def validate(directory: str):
	"""
	Validate a directory.\n
	Success flag is 'True' if 'directory' exists, is a regular directory, has a read permission, and is not empty.
	"""
	success = False
	message = ""
	if not os.path.isdir(directory):
		message = f'"{directory}" does not exist'
	elif not os.access(directory, os.R_OK):
		message = f'"{directory}" does not have a read permission'
	elif not len(os.listdir(directory)) > 0:
		message = f'"{directory}" is empty'
	else:
		success = True
	return success, message

def validate_silent(directory: str):
	"""
	Silently validate a directory.\n
	Returns 'True' if 'directory' exists, is a regular directory, has a read permission, and is not empty.
	"""
	success, ignored = validate(directory)
	return success

def create(directory: str):
	"""
	Create a new directory.
	"""
	success = True
	message = ""
	try:
		if not os.path.exists(directory):
			os.mkdir(directory)
	except Exception as ex:
		success = False
		message = f'Cannot create "{directory}"'
		debug.debug.log_error(f"utils.directory.create() > {directory}", ex)
	return success, message

def remove(directory: str):
	"""
	Remove a directory.
	"""
	success = True
	message = ""
	try:
		if os.path.exists(directory):
			shutil.rmtree(directory)
	except Exception as ex:
		success = False
		message = f'Cannot remove "{directory}"'
		debug.debug.log_error(f"utils.directory.remove() > {directory}", ex)
	return success, message

def overwrite(directory: str):
	"""
	Overwrite a directory.
	"""
	success, message = remove(directory)
	if success:
		success, message = create(directory)
	return success, message

def create_multiple(directories: list[str]):
	"""
	Create multiple new directories.
	"""
	success = True
	message = ""
	for directory in directories:
		success, message = create(directory)
		if not success:
			break
	return success, message

def remove_multiple(directories: list[str]):
	"""
	Remove multiple directories.
	"""
	success = True
	message = ""
	for directory in directories:
		success, message = remove(directory)
		if not success:
			break
	return success, message

def remove_empty_recursively(directory: str):
	"""
	Recursively remove empty files and directories, starting from the specified directory.
	"""
	success = True
	message = ""
	current = ""
	try:
		for path, directories, files in os.walk(directory, topdown = False):
			for file in files:
				current = os.path.join(path, file)
				if os.path.isfile(current) and not os.stat(current).st_size > 0:
					os.remove(current)
			for directory in directories:
				current = os.path.join(path, directory)
				if os.path.isdir(current) and not len(os.listdir(current)) > 0:
					os.rmdir(current)
	except Exception as ex:
		success = False
		message = f'Cannot remove "{current}"'
		debug.debug.log_error(f"utils.directory.remove_empty_recursively() | {current}", ex)
	return success, message

def listdir(directory: str):
	"""
	List a directory.
	"""
	tmp = []
	if os.path.isdir(directory):
		tmp = os.listdir(directory)
	return tmp

# ----------------------------------------

class Directory:

	def __init__(self):
		"""
		Initialize a class for managing directories.
		"""
		self.initialize("")

	def initialize(self, root_directory: str):
		"""
		[Re]initialize.
		"""
		self.__root_directory: str = root_directory
		self.__directories: dict[config.Directory, str] = {}
		for key in config.Directory:
			self.__directories[key] = self.__init_subdirectory(key.value)

	def __init_subdirectory(self, dirname: str):
		"""
		Get the full path to a subdirectory in the root directory.
		"""
		return os.path.join(self.__root_directory, dirname)

	def get(self, key: config.Directory):
		"""
		Get the full path to a directory for the specified key.\n
		Returns an empty string if the specified key does not exist.
		"""
		directory = ""
		try:
			directory = self.__directories[key]
		except Exception as ex:
			debug.debug.log_error(f"utils.directory.Directory().get() > {key}", ex)
		return directory

	def setup(self):
		"""
		Create the required directory structure and change the working directory to the root directory.
		"""
		success, message = create_multiple([self.__root_directory, *self.__directories.values()])
		if success:
			os.chdir(self.__root_directory)
		return success, message

	def cleanup(self):
		"""
		Recursively remove empty files and directories, starting from the root directory.
		"""
		success, message = remove_empty_recursively(self.__root_directory)
		return success, message

	def init_tools_subdirectory(self, dirname: str):
		"""
		Create a new subdirectory in the tools directory.\n
		Returns an empty string on failure, and the full path of the created subdirectory on success.
		"""
		subdirectory = os.path.join(self.__directories[config.Directory.TOOLS], dirname)
		success, ignored = create(subdirectory)
		if not success:
			subdirectory = ""
		return subdirectory

	def init_tools_file(self, filename: str, extension = "txt", tools_subdirname = ""):
		"""
		Get the full path to a file in the tools directory or its subdirectory.
		"""
		return file.SafeFile(os.path.join(self.__directories[config.Directory.TOOLS], tools_subdirname, f"{filename}.{extension}"))

directory = Directory()
"""
Singleton class instance for managing directories.
"""
