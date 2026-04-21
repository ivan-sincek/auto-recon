#!/usr/bin/env python3

import ipaddress

def validate(ip: str):
	"""
	Validate an IP.
	"""
	success = True
	message = ""
	try:
		ipaddress.ip_address(ip)
	except Exception:
		message = f"Invalid IP: {ip}"
		success = False
	return success, message

def validate_silent(ip: str):
	"""
	Silently validate an IP.
	"""
	success, ignored = validate(ip)
	return success
