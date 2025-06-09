#!/usr/bin/env python3

from .utils import auto_recon, general, validate

import datetime

class Stopwatch:

	def __init__(self):
		self.__start = datetime.datetime.now()

	def stop(self):
		self.__end = datetime.datetime.now()
		print(f"Script has finished in {self.__end - self.__start}")

stopwatch = Stopwatch()

# ----------------------------------------

def main():
	success, args = validate.Validate().validate_args()
	if success:
		tool = auto_recon.AutoRecon(args)
		success, message = tool.setup()
		if not success:
			general.print_error(message)
		else:
			tool.run()
			stopwatch.stop()

if __name__ == "__main__":
	main()
