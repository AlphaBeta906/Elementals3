from random import randint

# Based on: https://en.wikipedia.org/wiki/Color_difference#Euclidean
def colorDistance(hex1, hex2):
	r1 = int(hex1[0], 16) + int(hex1[1], 16)
	g1 = int(hex1[2], 16) + int(hex1[3], 16)
	b1 = int(hex1[4], 16) + int(hex1[5], 16)

	r2 = int(hex2[0], 16) + int(hex2[1], 16)
	g2 = int(hex2[2], 16) + int(hex2[3], 16)
	b2 = int(hex2[4], 16) + int(hex2[5], 16)

	result = (r1 - r2) ^ 2 + (g1 - g2) ^ 2 + (b1 - b2) ^ 2

	return int(result/2)
	
def elementStrength(hex1):
	colors = 0
	
	for hex2 in ["FF0000", "00FF00", "0000FF"]:
		colors += abs(colorDistance(hex1, hex2))
	
	return colors

class Element:
	def __init__(self, generation:int, difficulty:int, color:str, date:str, creator:int):
		self.generation = generation
		self.difficulty = difficulty
		self.color = color
		self.date = date
		self.creator = creator
		
	def __dict__(self):
		return {"generation": self.generation,
  	        "difficulty": self.difficulty,
  	        "color": self.color,
  	        "date": self.date,
  	        "creator": self.creator}
		
	def getWatts(self, superElement:bool, upgrade:int):
		if superElement:
			superElement = 2
		else:
			superElement = 1
			
		return (self.generation * elementStrength(self.color) * upgrade * superElement) + randint(1, 10)
