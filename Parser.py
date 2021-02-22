import requests
from bs4 import BeautifulSoup
import smtplib 
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from Util import Announcement, Stock

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