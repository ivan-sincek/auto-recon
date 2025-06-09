#!/usr/bin/env python3

from . import array, config, debug, file

import enum, os, threading

PLACEHOLDER_EXCLUSIONS = "<exclusions/>"
PLACEHOLDER_DOMAIN     = "<domain/>"
PLACEHOLDER_KEY        = "<key/>"

class RegEx(enum.Enum):
	"""
	Enum containing RegEx filter keys.\n
	Edit or add more RegEx filters here.
	"""
	SUBDOMAIN = rf"^{PLACEHOLDER_EXCLUSIONS}(?:[^\s\.]+\.)*{PLACEHOLDER_DOMAIN}$"
	IP        = rf"^{PLACEHOLDER_EXCLUSIONS}(?:[^\s\.\:]+\.)*[^\s\.\:]+$" # NOTE: Excludes IPv6.
	EMAIL     = rf"^(?:[^\s\.]+\.)*[^\s\.]+\@{PLACEHOLDER_EXCLUSIONS}(?:[^\s\.]+\.)*{PLACEHOLDER_DOMAIN}$"

	def set(self, exclusions: list[str] = None, domain = ""):
		"""
		Set the filter.
		"""
		domain = domain.replace(r".", r"\.") if domain else r"[^\s\.]+"
		if not exclusions:
			exclusions = ""
		else:
			exclusions = ("|").join([f"{entry}$" for entry in exclusions])
			exclusions = exclusions.replace(r".", r"\.").replace(r"*\.", r".+\.")
			exclusions = f"(?!{exclusions})"
		value = self.value
		value = value.replace(PLACEHOLDER_DOMAIN, domain)
		value = value.replace(PLACEHOLDER_EXCLUSIONS, exclusions)
		return value

class JQ(enum.Enum):
	"""
	Enum containing JQ filter keys.\n
	Edit or add more JQ filters here.
	"""
	DNSRECON = f'(map(select(.type | test("^A$|^AAAA$|^CNAME$|^MX$|^NX$|^PTR$|^SRV$"))) | . - map(select(.address // "" | test("{PLACEHOLDER_EXCLUSIONS}"))) | . - map(select(.exchange // "" | test("{PLACEHOLDER_EXCLUSIONS}"))) | . - map(select(.name // "" | test("{PLACEHOLDER_EXCLUSIONS}"))) | . - map(select(.target // "" | test("{PLACEHOLDER_EXCLUSIONS}")))) + (map(select(.type | test("^TXT$")))) | .[]'
	HOST     = f'. - map(select(.{PLACEHOLDER_KEY}[] | test("{PLACEHOLDER_EXCLUSIONS}"))) | .[]'

	def set(self, exclusions: list[str] = None):
		"""
		Set the filter.
		"""
		if not exclusions:
			exclusions = "^$"
		else:
			exclusions = ("|").join([f"^{entry}$" for entry in exclusions])
			exclusions = exclusions.replace(r".", r"\.").replace(r"*\.", r".+\.").replace(r"\.", r"\\.")
		value = self.value
		value = value.replace(PLACEHOLDER_EXCLUSIONS, exclusions)
		return value

	@classmethod
	def replace_key(cls, query: str, new: str):
		"""
		Replace all occurrences of 'exclusion.PLACEHOLDER_KEY' in a filter with a new value.
		"""
		return query.replace(PLACEHOLDER_KEY, new)

# ----------------------------------------

class Exclusion:

	__EXCLUSIONS_FILENAME = "exclusions.txt"

	def __init__(self):
		"""
		Initialize a class for managing exclusions and filters.
		"""
		self.__lock = threading.Lock()
		self.initialize("")

	def initialize(self, root_directory: str, exclusions_file = "", domain = ""):
		"""
		[Re]initialize.
		"""
		self.__root_directory = root_directory
		self.__exclusions_file = self.__init_safe_file(self.__EXCLUSIONS_FILENAME)
		self.__exclusions = self.__read(exclusions_file)
		self.__save()
		self.__domain = domain
		self.__filters = self.__set()

	def __init_safe_file(self, filename: str):
		"""
		Initialize a thread-safe file in the config directory.
		"""
		return file.SafeFile(os.path.join(self.__root_directory, config.Directory.CONFIG.value, filename))

	def __read(self, exclusions_file: str):
		"""
		Read exclusions from an exclusions file.\n
		If restoring a session, the exclusions file from the config directory has priority over the specified file.
		"""
		tmp = []
		for path in [self.__exclusions_file.path, exclusions_file]:
			if file.validate_silent(path):
				tmp = array.unique(file.read(path))
				break
		return tmp

	def __save(self):
		"""
		Save exclusions to the exclusions file in the config directory.
		"""
		file.insert(self.__exclusions, self.__exclusions_file)

	def __set(self) -> dict[RegEx | JQ, str]:
		"""
		Initialize filters.
		"""
		tmp = {}
		for key in RegEx:
			tmp[key] = key.set(self.__exclusions, self.__domain)
		for key in JQ:
			tmp[key] = key.set(self.__exclusions)
		return tmp

	def get(self, key: RegEx | JQ):
		"""
		Get a filter for the specified key.\n
		Returns an empty string if the specified key does not exist.
		"""
		filter = ""
		try:
			filter = self.__filters[key]
		except Exception as ex:
			debug.debug.log_error(f"utils.filter.Filter().get() > {key}", ex)
		return filter

	def update(self, exclusions: list[str] | str):
		"""
		Update exclusions and filters.
		"""
		if exclusions:
			with self.__lock:
				if not isinstance(exclusions, list):
					exclusions = [exclusions]
				self.__exclusions = array.unique(self.__exclusions + exclusions)
				self.__save()
				self.__filters = self.__set()

	def should_filter(self):
		"""
		Returns 'True' if there are any exclusions.
		"""
		return bool(self.__exclusions)

exclusion = Exclusion()
"""
Singleton class instance for managing exclusions and filters.
"""
