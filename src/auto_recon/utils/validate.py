#!/usr/bin/env python3

from . import config, directory, file, general, url

import argparse, os, sys

class MyArgParser(argparse.ArgumentParser):

	def print_help(self):
		print(config.HEADING)
		print("")
		print("Usage:   auto-recon -d domain      -o out     [-s subdomains    ] [-r resolvers    ] [-w wordlist    ]")
		print("Example: auto-recon -d example.com -o results [-s subdomains.txt] [-r resolvers.txt] [-w wordlist.txt]")
		print("")
		print("DESCRIPTION")
		print("    Not another auto-reconnaissance framework")
		print("DOMAIN")
		print("    Fully qualified domain name to search")
		print("    -d, --domain = example.com | etc.")
		print("EXCLUSIONS")
		print("    File containing [wildcard] domains, subdomains, and IPs to exclude from the scope")
		print("    If restoring a session, the exclusions file from the output directory has priority over the specified file")
		print("    -e, --exclusions = exclusions.txt | etc.")
		print("NO FILTERING")
		print("    Do not limit the scope to the FQDN")
		print("    Exclusions are still being respected")
		print("    -nf, --no-filtering")
		print("SUBDOMAINS")
		print("    File containing subdomains to brute force DNS records")
		print("    -s, --subdomains = subdomains.txt | etc.")
		print("RESOLVERS")
		print("    File containing trusted DNS resolvers to resolve DNS records")
		print("    -r, --resolvers = resolvers.txt | etc.")
		print("WORDLIST")
		print("    Wordlist to brute force URL paths")
		print("    -w, --wordlist = wordlist.txt | etc.")
		print("COLLABORATOR")
		print("    Collaborator URL")
		print("    -c, --collaborator = https://xyz.interact.sh | https://xyz.burpcollaborator.net | etc.")
		print("THREADS")
		print("    Number of parallel tools to run per stage")
		print("    Default: 5")
		print("    -th, --threads = 10 | etc.")
		print("OUT")
		print("    Output directory")
		print("    -o, --out = results | etc.")
		print("RESTORE SESSION")
		print("    Restore the session from the last breakpoint")
		print("    -rs, --restore-session")

	def error(self, message: str):
		if len(sys.argv) > 1:
			print("Missing a mandatory option (-d, -o) and/or optional (-e, -nf, -s, -r, -w, -c, -th, -rs)")
			print("Use -h or --help for more info")
		else:
			self.print_help()
		exit()

class Validate:

	def __init__(self):
		"""
		Initialize a class for validating and managing CLI arguments.
		"""
		self.__parser = MyArgParser()
		self.__parser.add_argument("-d" , "--domain"         , required = True , type   = str         , default = ""   )
		self.__parser.add_argument("-e" , "--exclusions"     , required = False, type   = str         , default = ""   )
		self.__parser.add_argument("-nf", "--no-filtering"   , required = False, action = "store_true", default = False)
		self.__parser.add_argument("-s" , "--subdomains"     , required = False, type   = str         , default = ""   )
		self.__parser.add_argument("-r" , "--resolvers"      , required = False, type   = str         , default = ""   )
		self.__parser.add_argument("-w" , "--wordlist"       , required = False, type   = str         , default = ""   )
		self.__parser.add_argument("-c" , "--collaborator"   , required = False, type   = str         , default = ""   )
		self.__parser.add_argument("-th", "--threads"        , required = False, type   = str         , default = ""   )
		self.__parser.add_argument("-o" , "--out"            , required = True , type   = str         , default = ""   )
		self.__parser.add_argument("-rs", "--restore-session", required = False, action = "store_true", default = False)

	def validate_args(self) -> tuple[bool, argparse.Namespace]:
		"""
		Validate and return the CLI arguments.
		"""
		self.__success = True
		self.__args = self.__parser.parse_args()
		self.__validate_domain()
		self.__validate_exclusions()
		self.__validate_subdomains()
		self.__validate_resolvers()
		self.__validate_wordlist()
		self.__validate_collaborator()
		self.__validate_threads()
		self.__validate_out()
		return self.__success, self.__args

	def __error(self, message: str):
		"""
		Set the success flag to 'False' to prevent the main task from executing, and print an error message.
		"""
		self.__success = False
		general.print_error(message)

	# ------------------------------------

	def __validate_domain(self):
		"""
		Validate a domain name.
		"""
		tmp = url.extract_fqdn(self.__args.domain)
		if not tmp:
			self.__error(f"Invalid domain name: {self.__args.domain}")

	def __validate_exclusions(self):
		"""
		Validate a file containing exclusions.
		"""
		if self.__args.exclusions:
			success, message = file.validate(self.__args.exclusions)
			if not success:
				self.__error(message)

	def __validate_subdomains(self):
		"""
		Validate a file containing subdomains.
		"""
		if self.__args.subdomains:
			success, message = file.validate(self.__args.subdomains)
			if not success:
				self.__error(message)

	def __validate_resolvers(self):
		"""
		Validate a file containing DNS resolvers.
		"""
		if self.__args.resolvers:
			success, message = file.validate(self.__args.resolvers)
			if not success:
				self.__error(message)

	def __validate_wordlist(self):
		"""
		Validate a wordlist.
		"""
		if self.__args.wordlist:
			success, message = file.validate(self.__args.wordlist)
			if not success:
				self.__error(message)

	def __validate_collaborator(self):
		"""
		Validate a collaborator URL.
		"""
		if self.__args.collaborator:
			success, message = url.validate(self.__args.collaborator)
			if not success:
				self.__error(message)

	def __validate_threads(self):
		"""
		Validate a number of threads.
		"""
		tmp = 5
		if self.__args.threads:
			if not self.__args.threads.isdigit():
				self.__error("Number of parallel tools to run must be numeric")
			else:
				tmp = int(self.__args.threads)
				if tmp <= 0:
					self.__error("Number of parallel tools to run must be greater than zero")
		self.__args.threads = tmp

	def __validate_out(self):
		"""
		Validate an output directory.
		"""
		if self.__args.restore_session:
			success, message = directory.validate(self.__args.out)
			if not success:
				self.__error(message)
			else:
				self.__args.out = os.path.abspath(self.__args.out)
		elif self.__success:
			confirm = "yes"
			if os.path.isdir(self.__args.out):
				confirm = input(f'"{self.__args.out}" already exists, overwrite (yes): ')
			if confirm.lower() not in ["yes", "y"]:
				self.__success = False
			else:
				success, message = directory.overwrite(self.__args.out)
				if not success:
					self.__error(message)
				else:
					self.__args.out = os.path.abspath(self.__args.out)
