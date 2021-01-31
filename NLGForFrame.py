from DialogAct import DialogAct
from DialogActTypes import DialogActTypes
import random
from collections import defaultdict
import pdb

class NLGForFrame:
	def __init__(self):
		self.Name = "NLGForFrame"
		self.hellos = ['Hello, what can I get started for you?',
						'Hello how I can help you?']
		self.acknowledgements = ["Got it.  ",
								 "Okay.  ",
								 "Sure thing.  ",
								 "Alright.  "]

	def get_toppings_str(self, toppings):
		toppingStr = ""
		if toppings and len(toppings) > 0:
			toppings = list(toppings)
			if len(toppings) == 1:
				toppingStr += "with {}, ".format(toppings[0])
			else:
				toppingStr += "with "
				toppingStr += ", ".join([topping for topping in toppings[:-1]])
				toppingStr += " and {}, ".format(toppings[-1])
		return toppingStr

	def ground_pizza(self, dialogAct):
		outstr = ""
		toppingStr = ""
		if type(dialogAct.slot[1]==defaultdict):
			# simple frame, passed in a dict
			try:
				slots = dialogAct.slot[1]
			except KeyError:
				print("Pizza information not properly passed to NLG in dialogAct.")
			outstr += "I have a {} {} crust {} pizza, ".format(slots['size'],slots['crust'],slots['pizza_type'], toppingStr)

		# if slots['toppings']:
		else:
			try:
				pizza = dialogAct.slot[1]
			except KeyError:
				print("Pizza information not properly passed to NLG in dialogAct.")
			toppingStr = self.get_toppings_str(pizza.print_toppings)
			outstr += "I have a {} {} crust {} pizza, {}".format(pizza.size,pizza.crust,pizza.pizza_type, toppingStr)
		outstr += "is that right?"
		return outstr

	def ground_order(self, dialogAct):
		try:
			slots = dialogAct.slot[1]
			pizzas = dialogAct.slot[2]

		except KeyError:
			print("Pizza/Order information not properly passed to NLG in dialogAct.")

		num_pizzas = len(pizzas)
		outstr = ""
		if dialogAct.DialogActType == DialogActTypes.REQALTS:
			outstr += "I need you to confirm, do you want "
		else:
			outstr += "So that is "
		for i, pizza in enumerate(pizzas):
			toppings = list(pizza.toppings)
			if num_pizzas > 1 and i == num_pizzas-1:
				outstr += "and "
			outstr += "a {} {} crust {} pizza ".format(pizza.size, pizza.crust, pizza.pizza_type)
			outstr += self.get_toppings_str(toppings)
		if slots['modality'] == 'pick-up':
			outstr += "for {} for pick-up, is that right?".format(str.title(slots['name']))
		else:
			outstr += "for {} for delivery to {}, is that right?".format(str.title(slots['name']),str.title(slots['address']))
		return outstr

	def generate(self, dialogAct):
		outstr = ''
		# grounding via acknowledgement
		if (dialogAct.DialogActType == DialogActTypes.HELLO):
			outstr += random.choice(self.hellos)
		elif dialogAct.change:
			outstr += "Okay I've updated that.  "
		elif dialogAct.informedLast:
			outstr += random.choice(self.acknowledgements)
		
		# GOODBYE
		elif (dialogAct.DialogActType == DialogActTypes.GOODBYE):
			if dialogAct.slot:
				outstr += "Thanks, your total is ${:.2f}. We will see you in 15 minutes.  Goodbye".format(dialogAct.slot)
			else:
				outstr += "Ending session.  Thank you, goodbye."
		
		# CONFIRM
		elif (dialogAct.DialogActType == DialogActTypes.CONFIRM):
			outstr += "Yes."
		
		# DENY
		elif (dialogAct.DialogActType == DialogActTypes.DENY):
			outstr += "No."
		
		# INFORM
		if (dialogAct.DialogActType == DialogActTypes.INFORM):
			if (dialogAct.slot == "crust"):
				outstr += "We have thin, regular, deep dish, and gluten-free crusts."
			elif (dialogAct.slot == "size"):
				outstr += "We have small, medium, and large sizes."
			elif (dialogAct.slot == "pizza"):
				outstr += "Our specialty pizzas are Hawaiian, meat lovers, 4 cheese, pepperoni, veggie surpreme, and vegan."
			elif (type(dialogAct.slot) == tuple and dialogAct.slot[0] == 2):
				slots = dialogAct.slot[1]
				outstr += "I have an order on file for {} that is currently {}.".format(
							str.title(slots['name']),
								slots['order_status'])
			elif dialogAct.slot == 'revise_preferred':
				outstr += 'I have upddated your preferred order.  What else can I help you with?"'
			else:
				# update to modality of previous order
				outstr += "I have switched the delivery method of order number {} to {}.  What else can I help you with?".format(*dialogAct.slot)
			
		# REQUEST
		elif (dialogAct.DialogActType == DialogActTypes.REQUEST):
			if(dialogAct.slot == "anything_else"):
				outstr += "Would you like anything else?"
			elif(dialogAct.slot == "pizza_type"):
				outstr += "What kind of pizza would you like?"
			elif (dialogAct.slot == 'previous_address'):
				outstr += "What address can I add to that delivery order?"
			elif(dialogAct.slot == "crust"):
				outstr += "What crust type? We have thin, regular, deep dish, gluten free."
			elif(dialogAct.slot == "size"):
				outstr += "What size?"
			elif(type(dialogAct.slot) == tuple and dialogAct.slot[0]==0):
				outstr += self.ground_pizza(dialogAct)

				# slots = dialogAct.slot[1]
				# outstr += "I have a {} {} crust {} pizza, is that right?".format(slots['size'],slots['crust'],slots['pizza_type'])
			elif(dialogAct.slot == "name"):
				outstr += "Name?"
			elif(dialogAct.slot == "number"):
				outstr += "Phone Number?"
			elif(dialogAct.slot == "modality"):
				outstr += "Pick up or delivery?"
			elif(dialogAct.slot == "address"):
				outstr += "Address?"

			# Ground Full Order of Pizzas
			elif(type(dialogAct.slot)==tuple and dialogAct.slot[0]==1):
				outstr += self.ground_order(dialogAct)
			else:
				outstr += "Not implemented yet"

		# REQALTS
		elif (dialogAct.DialogActType == DialogActTypes.REQALTS):
			if not dialogAct.informedLast:
				outstr += "Sorry I didn't get that. "
			if dialogAct.slot == 'wildcard':
				outstr += 'What would you like to change?'
			elif(dialogAct.slot == "pizza_type"):
				outstr += "What kind of pizza would you like?"
			elif(dialogAct.slot == "crust"):
				outstr += "What crust type? We have thin, regular, deep dish, gluten free."
			elif(dialogAct.slot == "size"):
				outstr += "What size?"
			elif(type(dialogAct.slot) == tuple and dialogAct.slot[0]==0):
				outstr += self.ground_pizza(dialogAct)

				# slots = dialogAct.slot[1]
				# outstr += "I have a {} {} crust {} pizza, is that right?".format(slots['size'],slots['crust'],slots['pizza_type'])
			elif(dialogAct.slot == "name"):
				outstr += "Name?"
			elif(dialogAct.slot == "number"):
				outstr += "Phone Number?"
			elif(dialogAct.slot == "modality"):
				outstr += "Pick up or delivery?"
			elif(dialogAct.slot == "address"):
				outstr += "Address?"

			# Ground full order of Pizzas
			elif(type(dialogAct.slot)==tuple):
				outstr += self.ground_order(dialogAct)
				# slots = dialogAct.slot[1]
				# if slots['modality']=='pick-up':
				# 	outstr += "I need you to confirm, do you want a {} {} crust {} pizza, for {} for pick-up?".format(slots['size'],slots['crust'],slots['pizza_type'],slots['name'])
				# else:
				# 	outstr += "I need you to confirm, do you want a {} {} crust {} pizza, for {} for delivery to {}?".format(slots['size'],slots['crust'],slots['pizza_type'],str.title(slots['name']),str.title(slots['address']))
			else:
				# they asked to repeat before they had done anything
				outstr += "What kind of pizza can I add to your order?"
		elif  outstr == '':
			outstr += "Not implemented yet"
		return outstr