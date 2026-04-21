#!/usr/bin/env python3

from . import config, debug, file, general, jquery

import colorama, dataclasses, enum, os, platform, tabulate, threading

class Status(str, enum.Enum):
	"""
	Enum containing runtime statuses.
	"""
	PENDING   = "pending"
	RUNNING   = "running"
	COMPLETED = "completed"

	def get_color(self):
		"""
		Get the output color.
		"""
		mapping = {
			Status.PENDING  : colorama.Fore.WHITE,
			Status.RUNNING  : colorama.Fore.YELLOW,
			Status.COMPLETED: colorama.Fore.GREEN
		}
		return mapping[self]

@dataclasses.dataclass
class Tool:
	"""
	Class for storing tool details.
	"""
	base      : config.Tool
	identifier: int
	stage     : str
	status    : Status = Status.PENDING
	start     : str    = ""
	end       : str    = ""

@dataclasses.dataclass
class Runtime:
	"""
	Class for storing runtime details.
	"""
	version: str        = config.APP_VERSION
	stages : list[str ] = dataclasses.field(default_factory = list)
	tools  : list[Tool] = dataclasses.field(default_factory = list)

class Session:

	__SESSION_FILENAME = "session.json"

	def __init__(self):
		"""
		Initialize a class for managing the session.
		"""
		self.__lock = threading.Lock()
		self.__clear = "cls" if platform.system().lower() == "windows" else "clear"
		self.initialize("")

	def initialize(self, root_directory: str):
		"""
		[Re]initialize.
		"""
		self.__root_directory: str = root_directory
		self.__session_file: file.SafeFile = self.__init_safe_file(self.__SESSION_FILENAME)
		self.__session: Runtime = None

	def __init_safe_file(self, filename: str):
		"""
		Initialize a thread-safe file in the config directory.
		"""
		return file.SafeFile(os.path.join(self.__root_directory, config.Directory.CONFIG.value, filename))

	def new(self) -> tuple[bool, str]:
		"""
		Start a new session.
		"""
		success = True
		message = ""
		try:
			self.__session = Runtime()
			identifier = 0
			for stage, tools in config.RUNTIME.items():
				self.__session.stages.append(stage)
				for tool in tools:
					self.__session.tools.append(Tool(tool, identifier, stage))
					identifier += 1
		except Exception as ex:
			success = False
			message = "Cannot create a new session"
			debug.debug.log_error(f"utils.session.Session().new()", ex)
		return success, message

	def restore(self):
		"""
		Restore the session from the session file in the config directory.
		"""
		success = True
		message = ""
		try:
			self.__session = Runtime(**jquery.jload(self.__session_file))
			for i in range(len(self.__session.tools)):
				self.__session.tools[i] = Tool(**self.__session.tools[i])
				self.__session.tools[i].status = Status(self.__session.tools[i].status)
				self.__session.tools[i].base = config.Tool(**self.__session.tools[i].base)
				self.__session.tools[i].base.intrusive = config.Intrusive(self.__session.tools[i].base.intrusive)
		except Exception as ex:
			success = False
			message = f'Cannot restore the session from "{self.__session_file.path}"'
			debug.debug.log_error(f"utils.session.Session().restore() > {self.__session_file.path}", ex)
		return success, message

	def get_stages(self):
		"""
		Get stages.
		"""
		return self.__session.stages

	def get_stage_tools(self, stage: str) -> list[Tool]:
		"""
		Get pending and running tools for the specified stage.
		"""
		tmp = []
		for tool in self.__session.tools:
			if tool.stage == stage and tool.status != Status.COMPLETED:
				tmp.append(tool)
		return tmp

	def update(self, identifier: int, completed = False):
		"""
		Update a tool's status and start/end time for the specified ID, and then save and print the session.
		"""
		with self.__lock:
			now = general.get_timestamp()
			if completed:
				self.__session.tools[identifier].status = Status.COMPLETED
				self.__session.tools[identifier].end = now
			else:
				self.__session.tools[identifier].status = Status.RUNNING
				self.__session.tools[identifier].start = now
			self.__save()
			self.__print_as_table()

	def __save(self):
		"""
		Save the session to the session file in the config directory.
		"""
		file.insert(jquery.jdump(dataclasses.asdict(self.__session)), self.__session_file)

	def __print_as_table(self):
		"""
		Print the session in table format.
		"""
		headers = ["id", "stage", "tool", "status", "start", "end", "active", "intrusive"]
		tmp = []
		for tool in self.__session.tools:
			color = tool.status.get_color()
			row = {
				headers[0]: tool.identifier,
				headers[1]: tool.stage,
				headers[2]: tool.base.name,
				headers[3]: tool.status.value,
				headers[4]: tool.start,
				headers[5]: tool.end,
				headers[6]: "yes" if tool.base.active else "",
				headers[7]: tool.base.intrusive.value
			}
			tmp.append([color + str(row[key]) + colorama.Style.RESET_ALL for key in headers])
		os.system(self.__clear)
		print(tabulate.tabulate(tmp, headers, tablefmt = "outline", colalign = ("right", "left", "left", "left", "left", "left", "left", "left")))
		print(config.HEADING)

session = Session()
"""
Singleton class instance for managing the session.
"""
