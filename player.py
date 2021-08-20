class Player:
	def __init__(self, elements:list=["Fire", "Water", "Earth", "Air"], watts:int=100, upgrade:int=0):
		self.elements = elements
		self.watts = watts
		self.upgrade = upgrade
		
	def __dict__(self):
		return {"elements": self.elements,
						"watts": self.watts,
						"upgrade": self.upgrade}
	
	def addElement(self, element):
		self.elements.append(element)
