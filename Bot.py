import time
import webbrowser
from PIL import Image, ImageGrab
import pyautogui
import pytesseract

class Bot():
	def __init__(self):
		self.target_colors = {"yellow_add_to_cart":(255, 224, 0), "blue_go_to_cart":(0, 70, 190), "yellow_checkout": (255, 224, 0)}
		self.texts = {"yellow_add_to_cart":'WF Add to Cart', "blue_go_to_cart":'‘Goto Cart', "yellow_checkout":'Checkout'}

	def openSite(self, site):
		chrome_path = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s'
		webbrowser.get(chrome_path).open(site)

	def doAction(self, action, param):
		if action == "scroll":
			pyautogui.scroll(param)
		elif action == "click":
			pyautogui.moveTo(param[0], param[1], duration=1)
			#pyautogui.click()

	def grabColor(self):
		image = ImageGrab.grab()
		for y in range(470, 520, 10):
			for x in range(1300, 1700, 10): #
				color = image.getpixel((x, y))
				print(x,y,color)
		#if len(targs) == 0:
			#return None

	def screenshot(self, name, xb, yb):
		image1 = None
		if xb != None and yb != None:
			print(xb, yb)
			avgPT1 = (int((xb["min"][0] + yb["min"][-1]) / 2), int((yb["min"][0] + xb["min"][-1]) / 2)) 
			avgPT2 = (int((xb["max"][0] + yb["max"][-1]) / 2), int((yb["max"][0] + xb["max"][-1]) / 2))
			print('screenshot:',avgPT1, avgPT2)
			image1 = ImageGrab.grab(bbox=(avgPT1[0],avgPT1[1],avgPT2[0], avgPT2[1]))
			if not os.path.isdir('tmp'):
				os.mkdir('tmp')
		else:
			image1 = ImageGrab.grab(bbox=None)
			if not os.path.isdir('screens'):
				os.mkdir('screens')
		image1.save(name)

	def verifyBoundaries(self, x_boundaries, y_boundaries):
		if (x_boundaries["min"][0] == y_boundaries["min"][-1] and x_boundaries["max"][0] == y_boundaries["max"][-1]):
			return True
		elif abs(x_boundaries["min"][0] - y_boundaries["min"][-1]) < 50 and abs(x_boundaries["max"][0] - y_boundaries["max"][-1]) < 50:
			return True
		return False

	def parseImageText(self, name):
		pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"
		text = pytesseract.image_to_string(name).replace("\n\x0c","")
		print(text)
		os.remove(name)
		return text

	def getPositionOfTarget(self, target): # Target is color of add to cart button
		targ_color = self.target_colors[target]
		image = ImageGrab.grab()
		targs = []
		for y in range(0, 1040, 10):
			for x in range(0, 1900, 10): #
				color = image.getpixel((x, y))
				if color == targ_color:
					targs.append((x,y))
		print(target, f': found {len(targs)} targets')
		if len(targs) == 0:
			return None
		x_boundaries = {"min":min(targs), "max":max(targs)}
		y_boundaries = {"min":min([(t[-1],t[0]) for t in targs]), "max":max([(t[-1],t[0]) for t in targs])}
		if self.verifyBoundaries(x_boundaries, y_boundaries):
			name = f'tmp/{target}.png'
			self.screenshot(name, x_boundaries, y_boundaries)
			text = self.parseImageText(name)
			if text == self.texts[target]:
				click_pos = (int((x_boundaries["min"][0] + x_boundaries["max"][0])/2), int((y_boundaries["min"][0] + y_boundaries["max"][0])/2)) #x,y
				return click_pos
			else:
				print(f'{text} != {self.texts[target]}')
		return None

	def auto_bestbuy(self):
		# Add to cart
		i = 0
		add_to_cart_click_pos = None
		while i < 3 and add_to_cart_click_pos == None: # SCROLL 3 TIMES BEFORE GIVING UP SEARCH
			add_to_cart_click_pos = self.getPositionOfTarget("yellow_add_to_cart")
			if add_to_cart_click_pos == None:
				self.doAction("scroll", -1000)
				time.sleep(1)
			i += 1
		add_to_cart_click_pos = (self.getPositionOfTarget("yellow_add_to_cart") if add_to_cart_click_pos == None else add_to_cart_click_pos)
		if add_to_cart_click_pos != None:
			self.doAction("click", add_to_cart_click_pos)
		else:
			print("Error at add to cart")
			return False
		print("add to cart:",add_to_cart_click_pos)
		time.sleep(1.5)
		# Go to cart
		i = 0
		go_to_cart_click_pos = None
		while i < 5 and go_to_cart_click_pos == None: # Wait 5 seconds maximum
			go_to_cart_click_pos = self.getPositionOfTarget("blue_go_to_cart")
			if go_to_cart_click_pos == None:
				time.sleep(1)
			i += 1
		if go_to_cart_click_pos != None:
			self.doAction("click", go_to_cart_click_pos)
		else:
			print("Error at go to cart")
			return False
		print("go to cart:",go_to_cart_click_pos)
		time.sleep(3) # Possibile sign up click at bottom of screen before load
		# Checkout
		i = 0
		checkout_click_pos = None
		while i < 5 and checkout_click_pos == None: # Wait 5 seconds maximum
			checkout_click_pos = self.getPositionOfTarget("yellow_checkout")
			if checkout_click_pos == None:
				time.sleep(1)
			i += 1
		if checkout_click_pos != None:
			self.doAction("click", checkout_click_pos)
		else:
			print("Error at checkout")
			return False
		print("checkout:",checkout_click_pos)
		time.sleep(2.5)
		# Continue as Guest
		self.doAction("click",(1245,386))
		time.sleep(1.5)

	def run(self, triggered_mode):
		eval(f'self.auto_{triggered_mode}')