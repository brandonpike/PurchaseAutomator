import os,sys
import time
from Parser import Parser
from Bot import Bot
from Util import VendorHub

def main(args):
	time.sleep(2) # Give user a moment to tab into site

	valid_modes = ["generic", "bestbuy", "psdirect", "all_vendors"]

	mode = None
	if len(args) == 1:
		mode = args[0]
	else:
		mode = "all_vendors"

	if mode not in valid_modes:
		print(f'Error, {mode} is not a valid mode.')
		return

	vendorhub = VendorHub()
	parser = Parser(vendorhub, mode)
	bot = Bot(vendorhub)

	flag = True
	while flag:
		actions_required = parser.parse()
		print(f'Actions required -> {actions_required}')

		for action in actions_required:
			result = bot.run(action)
			print(result)

		time.sleep(30) # Ping sites every 30 seconds

if __name__ == "__main__":
	args = sys.argv[1:];
	if len(args) == 1:
		main(args);
	else:
		main([]);
