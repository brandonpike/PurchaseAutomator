import os,sys
import time
from Parser import Parser
from Bot import Bot

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

	parser = Parser(mode)
	return
	bot = Bot()

	flag = True
	while flag:
		actions_required = parser.parse()

		for action in actions_required:
			bot.openSite(action)
			bot.run(mode)

		time.sleep(30) # Ping sites every 30 seconds

if __name__ == "__main__":
	args = sys.argv[1:];
	if len(args) == 1:
		main(args);
	else:
		main([]);