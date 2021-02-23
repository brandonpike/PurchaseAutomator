import os,sys
import time
import webbrowser
from PIL import Image, ImageGrab
import pyautogui
import pytesseract
from Util import VendorHub

class Bot():
	def __init__(self, vh):
		self.target_colors = {"yellow_add_to_cart":(255, 224, 0), "blue_go_to_cart":(0, 70, 190), "yellow_checkout": (255, 224, 0)}
		self.texts = {"yellow_add_to_cart":'WF Add to Cart', "blue_go_to_cart":'‘Goto Cart', "yellow_checkout":'Checkout'}
		self.VH = vh

	def openSite(self, action_to_take):
		site = self.VH.URLS[action_to_take]
		chrome_path = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe %s'
		webbrowser.get(chrome_path).open(site)

	def doAction(self, action, params): # scroll param = [int], click params = [(x,y),target]
		if action == "scroll":
			pyautogui.scroll(params[0])
		elif action == "click":
			if len(params) != 2:
				print(f"Error in doAction - {action}")
				return False
			pyautogui.moveTo(params[0][0], params[0][1], duration=1)
			if params[1] == "yellow_add_to_cart":
				print(f'{params[1]} <- verification target')
				verification = self.getPositionOfTarget(params[1])
				if verification != None and verification != params[0]:
					print(f'{params[0]} != {verification}, choosing second grab.')
					pyautogui.moveTo(verification[0], verification[1],duration=0.2)
			pyautogui.click()

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
			if avgPT1[0] == avgPT2[0] or avgPT1[1] == avgPT2[1]:
				return None
			if not os.path.isdir('tmp'):
				os.mkdir('tmp')
		else:
			image1 = ImageGrab.grab(bbox=None)
			if not os.path.isdir('screens'):
				os.mkdir('screens')
		print(f'{(avgPT1[0],avgPT1[1],avgPT2[0], avgPT2[1])} <- bounds of screenshot')
		image1.save(name)
		return True

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
		#os.remove(name)
		return text

	def getPositionOfTarget(self, target): # Target is color of add to cart button
		targ_color = self.target_colors[target]
		image = ImageGrab.grab()
		targs = []
		image.save('tmp/getPositionOfTarget.png')
		for y in range(0, 1080, 5):
			for x in range(0, 1920, 10): #
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
			sc_result = self.screenshot(name, x_boundaries, y_boundaries)
			if sc_result == None:
				return self.getPositionOfTarget(target)
			actual_text,expected_text = self.parseImageText(name), self.texts[target]
			text_likeness = (stringLikeness(actual_text, expected_text) if len(actual_text) < len(expected_text) else stringLikeness(expected_text, actual_text))\
									if actual_text != expected_text else 1.0
			if text_likeness > .75:
				click_pos = (int((x_boundaries["min"][0] + x_boundaries["max"][0])/2), int((y_boundaries["min"][0] + y_boundaries["max"][0])/2)) #x,y
				return click_pos
			else:
				print(f'{actual_text} != {expected_text}')
		else:
			print(f'Boundary error | {x_boundaries}, {y_boundaries}\n{targs}')
		return None

	def auto_bestbuy(self):
		# Add to cart
		i = 0
		target = "yellow_add_to_cart"
		atc_click_pos = None
		while i < 4 and atc_click_pos == None: # SCROLL 3 TIMES BEFORE GIVING UP SEARCH
			atc_click_pos = self.getPositionOfTarget(target)
			if atc_click_pos == None:
				self.doAction("scroll", [-1000, target])
				time.sleep(1)
			i += 1
		atc_click_pos = (self.getPositionOfTarget(target) if atc_click_pos == None else atc_click_pos)
		if atc_click_pos != None:
			self.doAction("click", [atc_click_pos, target])
		else:
			print("Error at add to cart")
			return False
		print("add to cart:",atc_click_pos)
		time.sleep(1.5)
		# Go to cart
		i = 0
		target = "blue_go_to_cart"
		gtc_click_pos = None
		while i < 5 and gtc_click_pos == None: # Wait 5 seconds maximum
			gtc_click_pos = self.getPositionOfTarget(target)
			if gtc_click_pos == None:
				time.sleep(1)
			i += 1
		if gtc_click_pos != None:
			self.doAction("click", [gtc_click_pos, target])
		else:
			print("Error at go to cart")
			return False
		print("go to cart:",gtc_click_pos)
		time.sleep(3) # Possibile sign up click at bottom of screen before load
		# Checkout
		i = 0
		target = "yellow_checkout"
		ch_click_pos = None
		while i < 5 and ch_click_pos == None: # Wait 5 seconds maximum
			ch_click_pos = self.getPositionOfTarget(target)
			if ch_click_pos == None:
				time.sleep(1)
			i += 1
		if ch_click_pos != None:
			self.doAction("click", [ch_click_pos, target])
		else:
			print("Error at checkout")
			return False
		print("checkout:",ch_click_pos)
		time.sleep(2.5)
		# Continue as Guest
		self.doAction("click",[(1245,386),None])
		time.sleep(1.5)

	def run(self, action_to_take):
		self.openSite(action_to_take)
		time.sleep(2) # Wait for site load
		pyautogui.moveTo(1000,500,duration=0)
		return eval(f'self.auto_{action_to_take}')()

def stringLikeness(s1, s2):
	L = [[0 for j in range(len(s2))] for i in range(len(s1))]
	cur = 0
	ret = []

	for i in range(len(s1)):
		for j in range(len(s2)):
			if s1[i] == s2[j]:
				if i == 0 or j == 0:
					L[i][j] = 1
				else:
					L[i][j] = L[i - 1][j - 1] + 1
				if L[i][j] > cur:
					cur = L[i][j]
					ret = [x for x in s1[i-cur+1:i+1]]
				elif L[i][j] == cur:
					#for z,k in zip(ret,s1[i-cur+1:i+1]):
						#print(ret,s1[i-cur+1:i+1],z,k)
					for x1,x2 in zip(ret,s1[i-cur+1:i+1]):
						ret.append(x2)
			else:
				L[i][j] = 0
	return len(ret)/len(s2)