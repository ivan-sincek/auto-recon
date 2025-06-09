#!/usr/bin/env python3

from . import array, config, debug, file

import concurrent.futures, dataclasses, subprocess

QUOTE = '"'

def set_opt(value: str | int | float, opt = "", escape = True):
	"""
	Cast a value to a string, enclose it in quotes, escape any inner quotes, and append it to an option - if specified.
	"""
	value = str(value)
	if value:
		if escape:
			value = QUOTE + value.replace(QUOTE, f"\\{QUOTE}") + QUOTE
		if opt:
			value = f"{opt}{value}" if opt.endswith("=") else f"{opt} {value}"
	return value

PLACEHOLDER = "<placeholder/>"
"""
A placeholder that will be replaced in 'run.multiple()' with each entry from the 'config.TXT' file.
"""

def replace_placeholder(cmd: list[str], new = "") -> list[str]:
	"""
	Replace all occurrences of 'tool.PLACEHOLDER' in each part of the command with a new value.
	"""
	tmp = []
	for part in cmd:
		if PLACEHOLDER in part:
			part = part.replace(PLACEHOLDER, new)
		tmp.append(part)
	return tmp

# ----------------------------------------

@dataclasses.dataclass
class Result:
	"""
	Class for storing a result.
	"""
	response: str
	data: str

def single(cmd: list[str], out: file.SafeFile = None, data = ""):
	"""
	Run a tool.
	"""
	cmd = array.join(cmd)
	response = subprocess.run(cmd, shell = True, stdout = subprocess.PIPE, stderr = subprocess.STDOUT).stdout
	if response:
		response = response.decode(file.ENCODING)
		if out:
			file.append(response, out)
		debug.debug.log_debug(cmd, response)
	return Result(response, data)

def multiple(cmd: list[str], key: config.TXT, out: file.SafeFile = None, threads = 5) -> list[Result]:
	"""
	Run a tool multiple times.
	"""
	tmp = []
	with concurrent.futures.ThreadPoolExecutor(max_workers = threads) as executor:
		subprocesses = []
		for entry in file.read(file.file.get(key)):
			subprocesses.append(executor.submit(single, replace_placeholder(cmd, entry), out, entry))
		for subprocess in concurrent.futures.as_completed(subprocesses):
			result: Result = subprocess.result()
			tmp.append(result)
	return tmp
