#!/usr/bin/env python3

from . import grep

import tldextract, urllib.parse

URL_SCHEME_WHITELIST = ["https", "http"]
MIN_PORT_NUM         = 1
MAX_PORT_NUM         = 65535

# ----------------------------------------

def validate(url: str):
	"""
	Validate a URL.
	"""
	success = False
	message = ""
	tmp = urllib.parse.urlsplit(url)
	if not tmp.scheme:
		message = f"URL scheme is required: {url}"
	elif tmp.scheme not in URL_SCHEME_WHITELIST:
		message = f"Supported URL schemes are 'https' and 'http': {url}"
	elif not tmp.netloc:
		message = f"Invalid domain name: {url}"
	elif tmp.port and (tmp.port < MIN_PORT_NUM or tmp.port > MAX_PORT_NUM):
		message = f"Port number is out of range: {url}"
	else:
		success = True
	return success, message

def validate_silent(url: str):
	"""
	Silently validate a URL.
	"""
	success, ignored = validate(url)
	return success

def extract_fqdn(url: str) -> str:
	"""
	Extract the fully qualified domain name (FQDN) from a URL.\n
	Returns an empty string on failure.
	"""
	tmp = ""
	obj = tldextract.extract(url)
	if obj.fqdn:
		tmp = obj.fqdn.lower()
	return tmp

def extract_netloc(url: str):
	"""
	Extract the domain name and port number from a URL.\n
	If the port number is not specified, set the default port number based on the URL scheme.\n
	Returns an empty string and zero on failure.
	"""
	domain, port = "", 0
	if domain := extract_fqdn(url):
		if ports := grep.find(url, (r"(?<={0}\:)\d{{1,5}}").format(domain.replace(r".", r"\."))):
			port = int(ports[0])
		elif schemes := grep.find(url, r"^.+(?=\:\/\/)"):
			port = 443 if schemes[0].lower() == "https" else 80
	return domain, port
