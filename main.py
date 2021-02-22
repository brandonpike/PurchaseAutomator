import requests
from bs4 import BeautifulSoup
import time
import smtplib 
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import webbrowser
from PIL import Image, ImageGrab
import pyautogui
import os,sys
import pytesseract

class Announcement():
	def __init__(self):
		self.messages = []
	def add(self, name, status):
		cleaned = name.replace("Console Digital Edition : ","")
		self.messages.append(f'{cleaned} is now {status} !')
	def getMessage(self):
		s = "Ps5 Stock Updates\n(Digital Edition Only)\n\n"
		for i,message in enumerate(self.messages):
			s += message
			if i != self.size() - 1:
				s += "\n\n"
		return s
	def size(self):
		return len(self.messages)

class Stock():
	def __init__(self, name="", status="", price="", updated=""):
		self.name = name
		self.status = status
		self.price = price
		self.updated = updated
		self.valid = True
	def update(self,i,value):
		value = value.strip()
		if i == 0:
			self.name = value
		elif i == 1:
			self.status = value
		elif i == 2:
			self.price = value
		elif i == 3:
			self.updated = value
	def __str__(self):
		return f'{self.name} | {self.status} | {self.price} | {self.updated}'

class Parser():
	def __init__(self, mode=None):
		self.mode = mode
		self.data = {}
		self.email,self.password = self.readLogin()
		self.contact_list = self.readContactList()
		self.service_emails = {
								"att":"@txt.att.net",
							   "tmobile":"@tmomail.net",
							   "verizon":"@vtext.com"
							   }
		self.headers = {'User-Agent': 'Mozilla/5.0'}
		self.URLS = {
					"generic":"https://www.nowinstock.net/videogaming/consoles/sonyps5/",
					"bestbuy":"https://www.bestbuy.com/site/whirlpool-24-6-cu-ft-side-by-side-refrigerator-stainless-steel/5991300.p?skuId=5991300",#"https://www.bestbuy.com/site/sony-playstation-5-digital-edition-console/6430161.p?skuId=6430161"
					"psdirect":"https://direct.playstation.com/en-us/consoles/console/playstation5-digital-edition-console.3005817"
					}
		self.first_parse = True

	def readLogin(self):
		login = []
		file_name = "login.txt"
		file = open(file_name,'r')
		for line in file:
			clean = line.replace("\n","")
			login.append(clean)

		print(login)

		return login #user,pass

	def readContactList(self):
		contacts = {}
		file_name = "contacts.txt"
		file = open(file_name,'r')
		category = None
		for line in file:
			clean = line.replace("\n","")
			if '\t' not in line:
				category = clean.replace(":","")
			else:
				clean = clean.replace("\t","")
				contacts[category] = clean.split(',')
		#print(contacts)
		return contacts

	def update(self, newData):

		announcement = Announcement()
		for site in newData:
			if self.first_parse == True:
				self.first_parse = False
				break
			if site not in self.data:
				for s in newData[site]:
					announcement.add(s.name, s.status)
				continue
			for s in newData[site]:
				old_s = None
				for os in self.data[site]:
					if os.name == s.name:
						old_s = os
						break
				if old_s == None:
					break
				if s.status != old_s.status:
					announcement.add(s.name, s.status)
		self.data = newData
		if announcement.size() > 0:
			print(announcement.messages)
			self.sendAnnouncement(announcement)
		else:
			print('No changes in stock.')
		print('---------------------------------------------------------------------')

	def sendAnnouncement(self, announcement):

		print(announcement.getMessage())
		
		smtp = "smtp.gmail.com" 
		port = 587
		server = smtplib.SMTP(smtp,port)
		server.starttls()
		server.login(self.email,self.password)

		for provider in self.contact_list:
			for contact in self.contact_list[provider]:
				sms_gateway = contact + self.service_emails[provider]
				print("target = ",sms_gateway)

				msg = MIMEMultipart()
				msg['From'] = self.email
				msg['To'] = sms_gateway

				msg['Subject'] = " "

				body = announcement.getMessage()#

				msg.attach(MIMEText(body, 'plain'))
				sms = msg.as_string()
				server.sendmail(self.email,sms_gateway,sms)

		server.quit()

	def parse(self): # returns actions required (boolean)
		actions_required = []
		parses = ([self.mode] if self.mode != "all_vendors" else [v for v in self.URLS if v != "generic"])
		for p in parses:
			action = eval(f'self.parse_{p}')
			if action == True:
				actions_required.append(p)
			elif p == "generic":
				self.update(action)
		return actions_required

	def parse_generic(self):
		newData = {}
		for site in self.URLS:
			stocks = [] 
			page = requests.get(self.URLS[site])
			soup = BeautifulSoup(page.content, "html.parser")
			data_container = soup.find(id="data")
			table = data_container.table
			rows = table.findChildren(['th','tr'])
			for row in rows:
				st = Stock()
				cells = row.findChildren('td')
				for i,cell in enumerate(cells):
					value = cell.string
					if value == None:
						split = str(cell).split('target="_blank">')
						if len(split) == 2:
							value = split[1].split("<")[0]
						else:
							value = None
					if value == "Not Tracking":
						st.valid = False
						break
					st.update(i,value)
				if st.valid == True and "Ebay" not in st.name and st.name != "" and "Console :" not in st.name and "Bundle:" not in st.name:
					stocks.append(st)
			newData[site] = stocks
		return newData

	def parse_bestbuy(self):
		url = self.URLS["bestbuy"]
		page = requests.get(url, headers=self.headers)
		soup = BeautifulSoup(page.text, 'html.parser')
		button = soup.find(class_='fulfillment-add-to-cart-button')
		btext = button.findChild().findChild().findChild().text
		return (False if btext == "Sold Out" else True)

	def parse_psdirect(self):
		btext = "Out of Stock"
		return (False if btext == "Out of Stock" else True)

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






'''image1 = ImageGrab.grab(bbox=(1072,364,1412,404))
name = "test.png"
image1.save(name)
text = bot.parseImageText(name)
print(text)
print([text])'''
'''for y in range(0, im.size[1], 5):
	for x in range(0, im.size[0], 10): #
		color = im.getpixel((x, y))
		print(x,y,color)'''