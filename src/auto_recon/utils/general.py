#!/usr/bin/env python3

import bot_safe_agents, datetime

def get_random_user_agent(as_header = False) -> str:
	"""
	Get a random user agent.
	"""
	user_agent = bot_safe_agents.get_random()
	return f"User-Agent: {user_agent}" if as_header else user_agent

def get_timestamp():
	"""
	Get the current timestamp.
	"""
	return datetime.datetime.now().strftime("%H:%M:%S")

def print_error(message: str):
	"""
	Print an error message.
	"""
	print(f"ERROR: {message}")
