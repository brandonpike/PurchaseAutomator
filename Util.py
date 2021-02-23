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

class VendorHub():
	def __init__(self):
		self.URLS = {
					"generic":"https://www.nowinstock.net/videogaming/consoles/sonyps5/",
					"bestbuy":"https://www.bestbuy.com/site/whirlpool-24-6-cu-ft-side-by-side-refrigerator-stainless-steel/5991300.p?skuId=5991300",#"https://www.bestbuy.com/site/sony-playstation-5-digital-edition-console/6430161.p?skuId=6430161",
					"psdirect":"https://direct.playstation.com/en-us/consoles/console/playstation5-digital-edition-console.3005817"
					}