#!/usr/bin/env python3

from . import config, debug

import os

class Wordlist:

	__WORDLISTS_DIRNAME = "wordlists"

	def __init__(self):
		"""
		Initialize a class for managing wordlists.
		"""
		self.__root_directory: str = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), self.__WORDLISTS_DIRNAME)
		self.__wordlists: dict[config.Wordlist, str] = {}
		for key in config.Wordlist:
			self.__wordlists[key] = self.__init_file(f"{key.value}.txt")

	def __init_file(self, filename: str):
		"""
		Initialize a file in the wordlists directory.
		"""
		return os.path.join(self.__root_directory, filename)

	def get(self, key: config.Wordlist):
		"""
		Get the full path to a wordlist for the specified key.\n
		Returns an empty string if the specified key does not exist.
		"""
		wordlist = ""
		try:
			wordlist = self.__wordlists[key]
		except Exception as ex:
			debug.debug.log_error(f"utils.wordlist.Wordlist().get() > {key}", ex)
		return wordlist

wordlist = Wordlist()
"""
Singleton class instance for managing wordlists.
"""
