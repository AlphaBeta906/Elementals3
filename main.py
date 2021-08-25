# Elementals3
# Created on: Aug 1, 2021

import discord
from discord.ext import commands
import json
import sys
from datetime import datetime
from random import randint, choice
import os
import atexit
import asyncio

from element import *
from player import *

intents = discord.Intents.default()
intents.members = True

client = commands.Bot(command_prefix='e!', intents=intents)
client.remove_command('help')

## FUNCTIONS ##

# Written by COVID-69#0457
def read(filename: str):
	try:
		with open(filename, 'r') as f:
			file = json.load(f)
		return file
	except:
		print("bruh")

# Written by COVID-69#0457
def write(data, filename: str) -> None:
	with open(filename, 'w') as f:
		json.dump(data, f, indent=2)

def save():
	a = {}
	for element in elements:
		a[element] = elements[element].__dict__()
		
	b = {}
	for player in players:
		b[player] = players[player].__dict__()
		
	write(a, "elements.json")
	write(reactions, "reactions.json")
	write(b, "players.json")
	
	print("\033[96mSaved!\033[m")

# Written by: Sathiya (https://stackoverflow.com/users/4402433/sathiya)
def combine_hex_values(hex1, hex2):
	d_items = sorted({hex1: 0.5, hex2: 0.5}.items())
	tot_weight = sum({hex1: 0.5, hex2: 0.5}.values())

	red = int(sum([int(k[:2], 16) * v for k, v in d_items]) / tot_weight)
	green = int(sum([int(k[2:4], 16) * v for k, v in d_items]) / tot_weight)
	blue = int(sum([int(k[4:6], 16) * v for k, v in d_items]) / tot_weight)
	zpad = lambda x: x if len(x) == 2 else '0' + x
	return zpad(hex(red)[2:]) + zpad(hex(green)[2:]) + zpad(hex(blue)[2:])

def find_combination(e1, e2, dictionary: dict):
  try:
  	if f"{e1}+{e2}" in dictionary.keys():
  		try:
  			return dictionary[f"{e1}+{e2}"]
  		except:
  			return False
  	else:
  		try:
  			return dictionary[f"{e2}+{e1}"]
  		except:
  			return False
  except: 
  	return False

def ifIn(thing: str, dictionary: dict, e1: str, e2: str):
	try:
		return thing in dictionary[f"{e1}+{e2}"]
	except:
		return False

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

def elementStats(hex):
  dark = abs(colorDistance(hex, "000000"))
  light = abs(colorDistance(hex, "FFFFFF"))
  
  red = abs(colorDistance(hex, "FF0000"))
  green = abs(colorDistance(hex, "00FF00"))
  blue = abs(colorDistance(hex, "0000FF"))
  
  return [red, green, blue, light, dark]

@atexit.register
def exit_handler():
	print('\033[98mBye.\033[m')
	save()

## VARIABLES ##
global elements, reactions, players
elements = {}
players = {}

a = read("elements.json")
for element in a:
	elements[element] = Element(a[element]["generation"], a[element]["difficulty"], a[element]["color"], a[element]["date"], a[element]["creator"])
	
print(elements["Fire"])
	
reactions = read("reactions.json")
b = read("players.json")

for player in b:
	players[player] = Player(b[player]["elements"], b[player]["watts"], b[player]["upgrade"])
	
print(player)

now = datetime.now()
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
print("date and time =", dt_string)
del dt_string

requests = {}
a = ""
lastElementCreated = {}

token = os.environ['token']

tips = [
    'Felling stuck? You should try going to Wikipeidia or Little Alchemy 2 to find how a cirtain element is made.',
    'Try exploring with combining elements.',
    'Dont make all combinations result in a new element.',
    'We have a wiki! https://elementals3.fandom.com/',
    'Running out of ideas? You can use other alchemy games to use as reference',
    'The time most elements are made is at the afternoon, specifically the hours 12:00 to 3:00',
    'The bot was made in August 1!',
    "The creator's birthday is August 20th, just one day behind Ninoy Aquino Day.",
    'If you are feeling stuck, just use a hint.',
    'The bot is based on a web-game called Elemental 3, which sadly died in 2018.',
    'The creator is friends with the creator EOD.'
]


## EVENTS ##
@client.event
async def on_ready():
	await client.change_presence(
	    status=discord.Status.idle,
	    activity=discord.Game(
	        name=f"e!help | There are {len(elements)} elements!"))

	save()

	print("\033[92mOnline\033[m")

## COMMANDS 2 : The epic rewrite ##
@client.event
async def on_message(message):
	if message.author.id != client.user.id:
		if message.content == "e!help":
			embed = discord.Embed(colour=0x6a0dad, title='Help')
			embed.add_field(name='e!combine {e1} {e2}',
												value="Combine two elements.\nAliases: c",
												inline=True)
			embed.add_field(name='e!request {e1} {e2} {result}',
												value="Request a result. Costs 15 watts.\nAliases: r",
												inline=True)
			embed.add_field(name='e!upvote {e1} {e2} {result}',
												value="Upvote a request. Costs 10 watts.\nAliases: u",
												inline=True)
			embed.add_field(name='e!downvote {e1} {e2} {result}',
													value="Downvote a request. Costs 10 watts.\nAliases: d",
												inline=True)
			embed.add_field(name='e!elemlist [index]',
												value="Show all elements.\nAliases: e, elements",
												inline=True)
			embed.add_field(
						name='e!hint {element}',
						value="Get a hint of how to create a element. Costs 20 watts.",
						inline=True)
			embed.add_field(name='e!inv [user]',
											value="Shows inventory of a user.\nAliases: inventory",
											inline=True)
			embed.add_field(
						name='e!active',
						value="Shows 10 random actve requests. Costs 25 watts.\nAliases: re",
						inline=True)
			embed.add_field(name='e!bal [user]',
												value="Shows balance of a user.\nAliases: balance",
												inline=True)
			embed.add_field(
						name='e!upgrade [upgrade]',
						value=
						"Shows the upgrade level of a user and upgrade's their level aswell.\nAliases: up",
						inline=True)
			embed.add_field(name='e!double {element}',
												value="Combines the element to itself.\nAliases: du",
												inline=True)
	
			embed.set_footer(text="{} is an required argument while [] is optional")
	
			await message.channel.send(embed=embed)
		elif message.content == "e!intro":
			embed = discord.Embed(
		    colour=0x0000a0,
		    title='Hello!',
		    description=
		    "Hello! This is the third iteration of **Elementals**, this time I am hosted on replit! Thanks replit!"
			)
	
			await message.channel.send(embed=embed)
		elif "+" == message.content[0]:
			try:
				element = message.content.replace("+", "").strip()
				
				try:
					result = find_combination(element, lastElementCreated[str(message.author.id)], reactions)
				
					print(result)
			
					if element not in elements:
						await message.channel.send("🔴 **ERROR**: Element 1 or 2 is does not exist")
					elif element not in players[str(message.author.id)].elements:
						await message.channel.send("🔴 **ERROR**: Element 1 or 2 is not in your inventory")
					elif result == False:
						await message.channel.send("🟡 **WARNING**: Result does not exist, to request one, press e!request.")
					else:
						if randint(1, 15) == 1:
							superElement = True
						else:
							superElement = False
							
						try:
							upgrade = players[str(message.author.id)]["upgrade"]
						except:
							upgrade = 1
			
						wattsAfterCreation = elements[result].getWatts(superElement, upgrade)
						
						if superElement:
							a = f"Luckily, you created a super element, so, you created {wattsAfterCreation} watts."
						else:
							a = f"You created {wattsAfterCreation} watts!"
			
						embed = discord.Embed(
							colour=int(elements[result].color, 16),
							title=f'You created {result}',
							description=a
						)
			
						embed.set_footer(text=f"Tip/Fun Fact: {choice(tips)}")
			
						if result not in players[str(message.author.id)].elements:
							players[str(message.author.id)].addElement(result)
							
						players[str(message.author.id)].watts += wattsAfterCreation
			
						await message.channel.send(embed=embed)
						del wattsAfterCreation
					
					lastElementCreated[str(message.author.id)] = result
				except:
					await message.channel.send("🔴 **ERROR**: You should create a element before using the + command")
			except:
				await message.channel.send("🔴 **ERROR**: You have a missing argument in your command")

			save()
		elif ("+" in message.content or "," in message.content or "\n" in message.content) and ("=" not in message.content and "==" not in message.content):
			print("AYYYYY")
			try:
				if "+" in message.content:
					e1 = message.content.split("+")[0].title().strip()
					e2 = message.content.split("+")[1].title().strip()
				elif "\n" in message.content:
					e1 = message.content.split("\n")[0].title().strip()
					e2 = message.content.split("\n")[1].title().strip()
				else:
					e1 = message.content.split(",")[0].title().strip()
					e2 = message.content.split(",")[1].title().strip()
					
				if str(message.author.id) not in players.keys():
					players[str(message.author.id)] = Player()
				else:
					print("HELEOOEJIDH")
		
				result = find_combination(e1, e2, reactions)
				
				print(result)
		
				if (e1 not in elements) or (e2 not in elements):
					await message.channel.send("🔴 **ERROR**: Element 1 or 2 is does not exist")
				elif (e1 not in players[str(
						message.author.id)].elements) or (e2 not in players[str(
								message.author.id)].elements):
					await message.channel.send("🔴 **ERROR**: Element 1 or 2 is not in your inventory")
				elif result == False:
					await message.channel.send("🟡 **WARNING**: Result does not exist, to request one, press e!request.")
				else:
					if randint(1, 15) == 1:
						superElement = True
					else:
						superElement = False
						
					try:
						upgrade = players[str(message.author.id)]["upgrade"]
					except:
						upgrade = 1
		
					wattsAfterCreation = elements[result].getWatts(superElement, upgrade)
					
					if superElement:
						a = f"Luckily, you created a super element, so, you created {wattsAfterCreation} watts."
					else:
						a = f"You created {wattsAfterCreation} watts!"
		
					embed = discord.Embed(
						colour=int(elements[result].color, 16),
						title=f'You created {result}',
						description=a
					)
		
					embed.set_footer(text=f"Tip/Fun Fact: {choice(tips)}")
		
					if result not in players[str(message.author.id)].elements:
						players[str(message.author.id)].addElement(result)
						
					players[str(message.author.id)].watts += wattsAfterCreation
		
					await message.channel.send(embed=embed)
					del wattsAfterCreation
		
					lastElementCreated[str(message.author.id)] = result
			except:
				await message.channel.send("🔴 **ERROR**: You have a missing argument in your command")

			save()
		elif "*" == message.content[0]:
			for x in range(1, int(message.content.replace("*", ""))):
			  result = find_combination(lastElementCreated[str(message.author.id)], lastElementCreated[str(message.author.id)], reactions)
	
			  if result == False:
				  await message.channel.send("🟡 **WARNING**: Result does not exist, to request one, press e!request.")
			  else:			
				  if randint(1, 15) == 1:
				  	superElement = True
				  else:
				  	superElement = False
				  	
				  try:
				  	upgrade = players[str(message.author.id)]["upgrade"]
				  except:
				  	upgrade = 1
				  	
				  wattsAfterCreation = elements[result].getWatts(superElement, upgrade)
				  
				  if superElement:
				  	a = f"Luckily, you created a super element, so, you created {wattsAfterCreation} watts."
				  else:
				  	a = f"You created {wattsAfterCreation} watts!"
	
				  embed = discord.Embed(
					  colour=int(elements[result].color, 16),
					  title=f'You created {result}',
					  description=a
			  	)
	
				  embed.set_footer(text=f"Tip/Fun Fact: {choice(tips)}")
	
				  if result not in players[str(message.author.id)].elements:
					  players[str(message.author.id)].addElement(result)
	
				  players[str(message.author.id)].watts += wattsAfterCreation
	
				  await message.channel.send(embed=embed)
				  del wattsAfterCreation
	
				  lastElementCreated[str(message.author.id)] = result
		elif ("+" in message.content or ", " in message.content or "\n" in message.content) and ("=" in message.content and "==" not in message.content):
			if str(message.author.id) not in players:
			  players[str(message.author.id)] = Player()
			else:
				print("HELEOOEJIDH")
					
			try:
				if "+" in message.content:
					e1 = message.content.split("=")[0].split("+")[0].title().strip()
					e2 = message.content.split("=")[0].split("+")[1].title().strip()
				elif "\n" in message.content:
					e1 = message.content.split("=")[0].split("\n")[0].title().strip()
					e2 = message.content.split("=")[0].split("\n")[1].title().strip()
				else:
					e1 = message.content.split("=")[0].split(",")[0].title().strip()
					e2 = message.content.split("=")[0].split(",")[1].title().strip()
					
				result = message.content.split("=")[1].title().strip()
				
				resultExists = find_combination(e1, e2, reactions)
	
				print(e1, e2, result)
				if e1 not in elements or e2 not in elements:
					await message.channel.send("🔴 **ERROR**: Element 1 or 2 is does not exist")
				elif resultExists != False:
					await message.channel.send("🔴 **ERROR**: Result does exist")
				elif ifIn(result, requests, e1, e2) == True:
					await message.channel.send("🔴 **ERROR**: Suggestion exists")
				elif len(result) > 256:
					await message.channel.send("🔴 **ERROR**: Element longer than 256 characters")
				elif players[str(message.author.id)].watts < 15:
					await message.channel.send("🟡 **WARNING**: You are too poor")
				else:
					if f"{e1}+{e2}" not in requests:
						requests[f"{e1}+{e2}"] = {result: [[], message.author.id]}
					else:
						requests[f"{e1}+{e2}"][result] = [[], message.author.id]
			
					embed = discord.Embed(
						title=f'You requested!',
						color=discord.Color.green(),
						description="Request has been added"
					)
			
					await message.channel.send(embed=embed)
			except:
				await message.channel.send("🔴 **ERROR**: You have a missing argument in your command")
		elif ("+" in message.content or ", " in message.content or "\n" in message.content) and "==" in message.content:
			if True:
				if "+" in message.content:
					e1 = message.content.split("=")[0].split("+")[0].title().strip()
					e2 = message.content.split("=")[0].split("+")[1].title().strip()
				elif "\n" in message.content:
					e1 = message.content.split("=")[0].split("\n")[0].title().strip()
					e2 = message.content.split("=")[0].split("\n")[1].title().strip()
				else:
					e1 = message.content.split("=")[0].split(",")[0].title().strip()
					e2 = message.content.split("=")[0].split(",")[1].title().strip()
					
				result = message.content.split("==")[1].title().strip()
				
				gen = 0
			
				print(e1, e2, result)
		
				if f"{e1}+{e2}" not in requests:
					await message.channel.send("🔴 **ERROR**: Request does not exist, to add one use e!request")
				elif message.author.id in requests[f"{e1}+{e2}"][result][0]:
					await message.channel.send("🟡 **WARNING**: You already voted")
				elif players[str(message.author.id)].watts < 10:
					await message.channel.send("🟡 **WARNING**: You are too poor")
				else:
					players[str(message.author.id)].watts -= 10
		
					if message.author.id not in [806714339943251999, 511108607043960843]:
						requests[f"{e1}+{e2}"][result][0].append(message.author.id)
					else:
						requests[f"{e1}+{e2}"][result][0].append("HAHA MONEY GO BRRRRR")
					
		
					if len(requests[f"{e1}+{e2}"][result][0]) == 2:
						if result not in elements:
							dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
		
							if elements[e1].generation > elements[e2].generation:
								gen = elements[e1].generation
							else:
								gen = elements[e2].generation
								
							if e1 == e2:
								diff = elements[e1].difficulty
							else:
								if elements[e1].difficulty > elements[e2].difficulty:
									diff = elements[e1].difficulty + 1
								else:
									diff = elements[e2].difficulty + 1
									
							print(elements["Fire"])
		
							elements[result] = Element(
								  date = dt_string,
									color = combine_hex_values(elements[e1].color, elements[e2].color),
									generation = gen + 1,
								  difficulty = diff,
									creator = requests[f"{e1}+{e2}"][result][1]
							)
		
							del gen, dt_string
		
							embed = discord.Embed(title=f"You voted!",
																		color=int(elements[result].color, 16),
																		description="You created a new element!")
		
							await message.channel.send(embed=embed)
		
							await client.change_presence(
									status=discord.Status.idle,
									activity=discord.Game(
											name=f"e!help | There are {len(elements)} elements!"))
						else:
							embed = discord.Embed(title=f"You voted!",
																		color=int(elements[result].color, 16),
																		description="You created a new result!")
		
							await message.channel.send(embed=embed)
		
						reactions[f"{e1}+{e2}"] = result
		
						del requests[f"{e1}+{e2}"]
					else:
						embed = discord.Embed(title=f"You voted!",
																	color=discord.Color.green(),
																	description="You voted!")
		
						await message.channel.send(embed=embed)
			#except:
			#	await message.channel.send("🔴 **ERROR**: You have a missing argument in your command")
			save()
		elif "?" == message.content[0] or "e!info" in message.content:
			if message.content not in ["?", "e!info"]:
				if "e!info" in message.content:
					element = message.content.replace("e!info", "").title().strip()
				else:
					element = message.content.replace("?", "").title().strip()
			else:
				element = choice(list(elements))
				
			if element not in elements:
				await message.channel.send("🔴 **ERROR**: Element does not exist")
			else:
				embed = discord.Embed(
					colour=int(elements[element].color, 16),
					title=element,
					description=f"Element {list(elements).index(element) + 1}"
				)
				embed.add_field(
					name='Time Created',
					value=elements[element].date + " (GMT-1)",
					inline=False
				)
				embed.add_field(
					name='Generation',
					value=str(elements[element].generation),
					inline=False
			  )
													
				embed.add_field(
					name='Complexity',
					value=str(elements[element].generation - 1),
					inline=False
				)
													
				embed.add_field(
					name='Difficulty',
				  value=str(elements[element].difficulty),
					inline=False
				)
													
				embed.add_field(
					name='Creator',
					value=client.get_user(elements[element].creator).name,
					inline=False
				)
		
				embed.set_footer(text=f"Tip/Fun Fact: {choice(tips)}")
					
				#downloadFile = downloadimages(element)
				#file = discord.File(downloadFile, filename="image.jpg")
		
				await message.channel.send(embed=embed)
		elif message.content == "e!stats":
			amount = 0
			
			for element in reactions.values():
				for reaction in element:
					amount += 1
				
			await message.channel.send(f"**Elements**: {len(elements)}\n**Reactions**: {amount}\n**Players**: {len(players)}")
			
			del amount
		elif "e!elemlist" in message.content:
			if len(elements) % 25 == 0:
				maxIndex = len(elements) / 25
			else:
				maxIndex = int(len(elements) / 25) + 1

			try:
				index = int(message.content.replace("e!elemlist", "").strip())
			except:
				index = 1
				
			if index > maxIndex:
				index = maxIndex

			newIndex = index - 1
			
			try:
				embed = discord.Embed(
			    colour=0xff0048,
				  title=f"Elements (Index:{index} / {maxIndex})",
				  description="\n".join(list(elements)[0+newIndex*25:newIndex*25+25])
			  )
			except:
				embed = discord.Embed(
			  	colour=0xff0048,
				  title=f"Elements (Index:{index} / {maxIndex})",
			    description="\n".join(list(elements)[0+newIndex*50:len(elements)])
			   )
			finally:
			  embed.set_footer(text=f"Tip/Fun Fact: {choice(tips)}")
			  
			  await message.channel.send(embed=embed)
		elif "e!elemsort" in message.content:
			try:
				value = message.content.replace("e!elemsort", "").strip()
				
				try:
					if value == "difficulty":
					  elements2 = {}
					  for element in elements:
						  elements2[element] = elements[element].difficulty
					else:
					 	 elements2 = {}
					 	 for element in elements:
						   elements2[element] = elements[element].generation
						
					elements2 = dict(sorted(elements2.items(), key=lambda x: x[1], reverse=True))
						
					embed = discord.Embed(
						colour=0xff0048,
						title=f"Elements sorted by {value}",
						description="\n".join(list(elements2)[0:25])
					)
					
				except:
					await message.channel.send("🔴 **ERROR**: Value does not exist")
				
				embed.set_footer(text=f"Tip/Fun Fact: {choice(tips)}")
				await message.channel.send(embed=embed)
			except:
				await message.channel.send("🔴 **ERROR**: You have a missing argument in your command")
		elif "e!inv" in message.content:	
			try:
				user = client.get_user(message.mentions[0].id)
			except:
				user = message.author

			if len(players[str(user.id)].elements) % 25 == 0:
				maxIndex = len(players[str(user.id)].elements) / 25
			else:
				maxIndex = int(len(players[str(user.id)].elements) / 25) + 1

			try:
				index = int(message.content.replace(f"e!inv", "").replace(f"<@{user.id}>", "").strip())
			except:
				index = 1

			if str(user.id) not in players:
				players[str(user.id)] = Player()
				
			if index > maxIndex:
				index = maxIndex
				
			newIndex = index - 1
	
			try:
				embed = discord.Embed(
			    colour=0x7242f5,
				  title=f"Inventory of {user.name} (Index:{index}/{maxIndex})",
				  description="\n".join(list(players[str(user.id)].elements)[0+newIndex*25:newIndex*25+25])
			  )
			except:
				embed = discord.Embed(
			  	colour=0x7242f5,
				  title=f"Inventory of {user.name} (Index:{index}/{maxIndex})",
			    description="\n".join(list(players[str(user.id)].elements)[0+newIndex*50:len(elements)])
			   )
			finally:
			  embed.set_footer(text=f"Tip/Fun Fact: {choice(tips)}")
			  
			  await message.channel.send(embed=embed)
		elif "e!hint" in message.content:
			if message.content != "e!hint":
				element = message.content.replace("e!hint", "").title().strip()
			else:
				element = choice(list(elements))
				
			a = ""
	
			if element not in reactions and element not in elements:
				await message.channel.send("🔴 **ERROR**: Element does not exist")
			elif element in ["Water", "Earth", "Air"]:
				await message.channel.send("🔴 **ERROR**: Primoridial elements doesn't have any solution")
			elif players[str(message.author.id)].watts < 20:
				message.channel.send("🟡 **WARNING**: You are too poor")
			else:
				players[str(message.author.id)].watts -= 20
	
				for reaction in reactions:
					if reactions[reaction] == element:
						if randint(1, 2) == 1:
							reaction = {"e1": reaction.split("+")[1], "e2": reaction.split("+")[0]}
						else:
							reaction = {"e1": reaction.split("+")[0], "e2": reaction.split("+")[1]}
							
						if (reaction["e1"] in players[str(message.author.id)].elements) and (reaction["e2"] in players[str(message.author.id)].elements):
							a += "\n✅ " + reaction["e1"] + "+" + str(len(reaction["e2"]) * "?")
						else:
							a += "\n❌ " + reaction["e1"] + "+" + str(len(reaction["e2"]) * "?")
	
				embed = discord.Embed(description=a,
															colour=0xdecd49,
															title=f"Hint for {element}")
	
				embed.set_footer(text=f"Tip/Fun Fact: {choice(tips)}")
	
				await message.channel.send(embed=embed)
			
			save()
		elif "e!reveal" in message.content:
			if message.content != "e!reveal":
				element = message.content.replace("e!reveal", "").title().strip()
			else:
				element = choice(list(elements))
	
			a = ""
	
			if element not in reactions and element not in elements:
				await message.channel.send("🔴 **ERROR**: Element does not exist")
			elif element in ["Water", "Earth", "Air"]:
				await message.channel.send("🔴 **ERROR**: Primoridial elements doesn't have any solution")
			elif players[str(message.author.id)].watts < 40:
				message.channel.send("🟡 **WARNING**: You are too poor")
			else:
				players[str(message.author.id)].watts -= 40
				
				for reaction in reactions:
				  if reactions[reaction] == element:
				  	if randint(1, 2) == 1:
				  		reaction = {"e1": reaction.split("+")[1], "e2": reaction.split("+")[0]}
				  	else:
				  		reaction = {"e1": reaction.split("+")[0], "e2": reaction.split("+")[1]}
				  		
				  	if (reaction["e1"] in players[str(message.author.id)].elements) and (reaction["e2"] in players[str(message.author.id)].elements):
				  	  a += "\n✅ " + reaction["e1"] + "+" + reaction["e2"]
				  	else:
				  		a += "\n❌ " + reaction["e1"] + "+" + reaction["e2"]
	
				embed = discord.Embed(description=a,
															colour=0xdecd49,
															title=f"Hint for {element}")
	
				embed.set_footer(text=f"Tip/Fun Fact: {choice(tips)}")
	
				await message.channel.send(embed=embed)
			
			save()
		elif message.content == "e!active":
			if players[str(message.author.id)].watts < 20:
				message.channel.send("🟡 **WARNING**: You are too poor")
			else:
				players[str(message.author.id)].watts -= 20
	
				if len(requests) != 0:
					a = []
	
					if len(requests) == 1:
						random = list(requests.keys())[0]
						if len(list(requests[random])) == 1:
							a.append(f"{random}={list(requests[random].keys())[0]}")
						else:
							a.append(
									f"{random}={choice(list(requests[random].keys()))}")
					elif len(requests) <= 10:
						for x in range(1, len(requests) + 1):
							random = choice(list(requests.keys()))
							if len(list(requests[random])) == 1:
								a.append(
										f"{random}={list(requests[random].keys())[0]}")
							else:
								a.append(
										f"{random}={choice(list(requests[random].keys()))}"
								)
					else:
						for x in range(1, 10):
							random = choice(list(requests.keys()))
							if len(list(requests[random])) == 1:
								a.append(
										f"{random}={list(requests[random].keys())[0]}")
							else:
								a.append(
										f"{random}={choice(list(requests[random].keys()))}"
								)
	
					if len(a) == 1:
						a = a[0]
					else:
						a = "\n".join(a)
	
				else:
					a = "There are no active requests!"
	
				embed = discord.Embed(description=a,
															colour=0xdb0d5c,
															title=f"Requests")
	
				await message.channel.send(embed=embed)
	
			save()
		elif "e!upgrade" in message.content:
			try:
				number = int(message.content.replace("e!upgrade", ""))
			except:
				number = 0
	
			if number == 0:
				embed = discord.Embed(colour=0x03fc1c, title="Upgrade")
	
				embed.add_field(name='Upgrade Level',
												value=players[str(message.author.id)].upgrade,
												inline=False)
	
				embed.set_footer(text=f"Tip/Fun Fact: {choice(tips)}")
	
				await message.channel.send(embed=embed)
			elif players[str(message.author.id)].watts < (
					players[str(message.author.id)].upgrade + number) * 100:
				await message.channel.send("🟡 **WARNING**: You are too poor")
			else:
				a = players[str(message.author.id)].upgrade + number
	
				embed = discord.Embed(
				  colour=0x03fc1c,
					title="Upgrade",
					description=f"You upgraded your combining machine to level {a}!"
				)
	
				players[str(message.author.id)].watts -= (
						players[str(message.author.id)].upgrade + number) * 100
				players[str(message.author.id)].upgrade += number
	
				embed.set_footer(text=f"Tip/Fun Fact: {choice(tips)}")
	
				await message.channel.send(embed=embed)
	
			save()
		elif "e!bal" in message.content:
			try:
				user = client.get_user(message.mentions[0].id)
			except:
				user = message.author
	
			embed = discord.Embed(colour=0x1cb7ff, title=f"Balance of {user.name}")
	
			embed.add_field(name='Watts',
											value=players[str(user.id)].watts,
											inline=True)
	
			await message.channel.send(embed=embed)
		elif "e!battle" in message.content:
			if message.content == "e!battle":
				await message.channel.send("🔴 **ERROR**: You have a missing argument in your command")
			else:
				user2 = client.get_user(message.mentions[0].id)
	
			if str(message.author.id) not in players:
				players[str(message.author.id)] = Player()
					
	
			if str(user2.id) not in players:
				players[str(user2.id)] = Player()
	
			player = [user2.id, message.author.id]
			playerping = [user2, message.author]
			playerhp = [
					int(players[str(message.author.id)].watts * 0.01),
					int(players[str(user2.id)].watts * 0.01)
			]
	
			def check(m):
				return (m.author.id == player[index % 2])
	
			if user2.id == message.author.id:
				await message.channel.send("🔴 **ERROR**: You are attacking yourself")
			else:
				playerelem = ["Fire", "Fire"]
				
				embed = discord.Embed(
				  colour=0x777777,
					title="The Battle Begins!",
					description=f"{user2.mention} prepare for battle!"
				)
				
				await message.channel.send(embed=embed)
	
				index = 1
	
				while True:
					embed = discord.Embed(
				  	colour=0x777777,
						title=f"Round {index}",
						description=f"Opponent:{playerhp[0]}\nDefendant:{playerhp[1]}\nRound {str(index)}: {playerping[index % 2].mention}!"
				  )
				  
					await message.channel.send(embed=embed)

					while True:
						embed = discord.Embed(
				  		colour=discord.Color.red(),
							title=f"Commands",
							description="**Commands**: elem, attack, heal"
				  	)
						await message.channel.send(embed=embed)
						msg = await client.wait_for('message', check=check)
						
						person = index % 2
	
						if msg.content.lower() == "elem":
							while True:
								while True:
									embed = discord.Embed(
				  					colour=discord.Color.purple(),
										title=f"ELEM",
										description="What element are you gonna choose?"
				  				)
				  
									await message.channel.send(embed=embed)
									msg = await client.wait_for('message', check=check)
	
									if msg.content.title() in players[str(
											player[person])].elements:
										playerelem[person] = msg.content.title()
										break
	
								break
							break
	
						elif msg.content.lower() == "attack":
							print(elementStats("FFF000")[2])
							
							weaknesses = elementStats(elements[playerelem[(person + 1) % 2]].color)[3] - elementStats(elements[playerelem[(person + 1) % 2]].color)[4]

							atk = (elements[playerelem[person]].generation * elementStats(elements[playerelem[person]].color)[0]) + randint(1, 10) + weaknesses
							
							if randint(1, 16) > elementStats(elements[playerelem[(person + 1) % 2]].color)[2]:
								embed = discord.Embed(
					  			colour=discord.Color.red(),
									title=f"ATTACK",
									description=f"You attacked your opponent using {playerelem[index % 2]}, making them lose {atk} HP!"
					  		)
					  		
								await message.channel.send(embed=embed)
								playerhp[(person + 1) % 2] -= atk
							else:
								embed = discord.Embed(
					  			colour=discord.Color.red(),
									title=f"ATTACK",
									description=f"You attacked, to bad your opponent dodged it."
					  		)
					  		
								await message.channel.send(embed=embed)
	
							break
						
						elif msg.content.lower() == "heal":
							health = (elements[playerelem[index % 2]].generation * elementStats(elements[playerelem[index % 2]].color)[1]) + randint(1, 10)
													
							embed = discord.Embed(
					  		colour=discord.Color.green(),
								title=f"HEAL",
								description=f"You healed yourself using {playerelem[person]}, making you get {health} HP!"
					  	)
					  	
							await message.channel.send(embed=embed)
							playerhp[(person + 1) % 2] += health
		
							break
						
					if message.content.lower() == "surrender":
						embed = discord.Embed(
					  	colour=0x777777,
							title=f"SURRENDER",
							description=f"You surrendered"
					  )
					  	
						await message.channel.send(embed=embed)
						
						break
	
					elif playerhp[index % 2] <= 0 or playerhp[index % 2] <= 0:
						await message.channel.send(playerping[index % 2].mention + " won.")
						break
	
					index += 1
		elif "e!leaderboard" in message.content:
			try:
				value = message.content.replace("e!leaderboard", "").strip()
				print(value)
				
				if value == "elem":
					value = "element inventory length"
					leaderboard = {}
					
					for player in players:
						leaderboard[player] = len(players[player].elements)
				else:
					value = "amount of watts"
					leaderboard = {}
					
					for player in players:
						leaderboard[player] = players[player].watts
			except:
				value = "element inventory length"
				leaderboard = {}
				
				for player in players:
					leaderboard[player] = len(players[player].elements)
				  
			a = f"This leaderboard is measured in {value}\n"
						
			leaderboard = dict(sorted(leaderboard.items(), key=lambda x: x[1], reverse=True))

			index = 1
			for player in list(leaderboard)[0:10]:
				a += f"\n**#{index} {client.get_user(int(player)).name}**: {leaderboard[player]}"
				index += 1

			embed = discord.Embed(
				colour=0x909090,
				title="Leaderboard",
				description=a
			)

			await message.channel.send(embed=embed)
		elif "e!profile" in message.content:
			try:
				user = client.get_user(message.mentions[0].id)
			except:
				user = message.author

			embed = discord.Embed(
        colour = 0xf5c542,
				title = f"Profile of {user.name}"
    	)
			embed.add_field(name='Watts',value=players[str(user.id)].watts, inline=False)
			embed.add_field(name='Total Elements',value=str(len(players[str(user.id)].elements)) + "/" + str(len(elements)), inline=False)
			embed.add_field(name='Percentage', value=str(int((len(players[str(user.id)].elements) / len(elements)) * 100)) + "%", inline=False)

			await message.channel.send(embed=embed)
		elif message.content == "e!add":
			await message.channel.send(
					"https://discord.com/api/oauth2/authorize?client_id=871201945677877298&permissions=0&scope=bot"
			)

client.run(token)
