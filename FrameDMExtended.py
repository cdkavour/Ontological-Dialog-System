from DialogFrameExtended import DialogFrameExtended
from DialogAct import DialogAct
from DialogActTypes import DialogActTypes
from collections import defaultdict
import math,random,json,pandas as pd

class Pizza:
	def __init__(self,pizza_type=None,crust=None,size=None,toppings=None,no_toppings=None):
		self.pizza_type = pizza_type
		self.crust = crust
		self.size = size
		self.toppings = toppings if toppings else set()
		self.no_toppings = no_toppings if no_toppings else set()
		self.price = None

	def populate_toppings(self):
		if not self.pizza_type == 'basic':
			toppings_map = {'hawaiian': {'pineapple','ham','mozzarella'},
						'meat lovers':{'mozzarella','pepperoni','ham','bacon','sausage'},
						'4 cheese':{'mozzarella','cheddar','swiss','provelone'},
						'pepperoni':{'mozzarella','pepperoni'},
						'veggie supreme':{'mozzarella','green peppers','red onions','mushrooms','black olives'},
						'vegan':{'green peppers','red onions','mushrooms','black olives'}}
			self.toppings = self.toppings.union(toppings_map[self.pizza_type])		
			self.toppings = self.toppings - self.no_toppings
			# don't include toppings that are a part of the regular specialty
			self.print_toppings = self.toppings.union('no {}'.format(topping) for topping in self.no_toppings) - toppings_map[self.pizza_type]
		else:
			self.pizza_type = 'basic'
			self.toppings = self.toppings - self.no_toppings
			self.print_toppings = self.toppings

	def calculate_pie_price(self,DB):
		# compute price based on specialty, size, and crust
		self.populate_toppings()
		# call the price db and calculate
		# the base price is the price of the crust
		price = DB.crusts.loc[DB.crusts['size'].eq(self.size) & DB.crusts.name.eq(self.crust)].price.values[0]
		# add on the price for all toppings
		for topping in self.toppings:
			price += DB.toppings.loc[DB.toppings.name.eq(topping)].price.values[0]
		return price

class DB:
	def __init__(self,path):
		with open(path) as f:
			self.data = json.load(f)
		self.path = path
		self.users = pd.DataFrame(self.data['users'])
		self.toppings = pd.DataFrame(self.data['toppings'])
		self.defaults = pd.DataFrame(self.data['defaults'])
		self.crusts = pd.DataFrame(self.data['crusts'])
		self.modality = self.data['modality'][0]
		self.order_idx = self.data['order_idx']
		self.modality_map = {'pick-up':'delivery',
							'delivery':'pick-up'}

	def save_new_order(self,slots,cost):
		num_digits = 3-int(math.log10(self.order_idx))+1
		confirmation_number = '0'*num_digits+str(self.order_idx)
		self.data['open_orders'].append({'name':slots['name'],
							'confirmation_number':confirmation_number,
							'modality':slots['modality'],
							'address':slots['address'], # this could be none, that's okay
							'status':'processing',
							'cost':cost})
		self.data['order_idx'] +=1
		with open(self.path,'w') as f:
			json.dump(self.data,f,indent=3)

	def get_order_status(self,name):
		last_order = [order for order in self.data['open_orders'] if order['name']==name][-1]
		return last_order['status']
	
	def update_modality(self,name):
		# try to update according to the name
		users_order = [i for i,order in enumerate(self.data['open_orders']) if order['name']==name][-1]
		to_modify = self.data['open_orders'].pop(users_order)
		to_modify['modality'] = self.modality_map[to_modify['modality']]
		self.data['open_orders'].append(to_modify)
		return (to_modify['confirmation_number'],to_modify['modality'])	

	def updatePreferred(self,name,pizza_type,crust,size,toppings,no_toppings):
		users_order = [i for i,user in enumerate(self.data['users']) if user['name']==name][-1]
		to_modify = self.data['users'].pop(users_order)
		new_preferred = Pizza(pizza_type=pizza_type,crust=crust,size=size,toppings=toppings,no_toppings=no_toppings)
		new_preferred.populate_toppings()
		to_modify['preferred'] = {'pizza_type':new_preferred.pizza_type,
								  'crust':new_preferred.crust,
								  'size':new_preferred.size,
								  'toppings':new_preferred.toppings}
		self.data['users'].append(to_modify)
	
	def get_preferred(self,name):
		user_order = [user for user in self.data['users'] if user['name']==name][0]['preferred']
		return user_order				

class FrameDMExtended:

	def __init__(self, NLU, NLG):
		self.NLU = NLU
		# define frame below, for example:
		self.PreviousSlots = defaultdict(lambda:None)
		self.DialogFrame = DialogFrameExtended()
		self.DB = DB('db.json')
		self.NLG = NLG
		self.NLU.setDB(self.DB)
		self.lastDialogAct = None
		self.pizzas = []

	def calculate_price(self):
		try:
			base_price = self.DB.modality[self.NLU.SemanticFrame.Slots['modality']]
			
			price = base_price
			for pizza in self.pizzas:
				price += pizza.calculate_pie_price(self.DB)

			#price = base_price + Pizza(pizza_type=self.NLU.SemanticFrame.Slots['pizza_type'],
			#							crust=self.NLU.SemanticFrame.Slots['crust'],
			#							size=self.NLU.SemanticFrame.Slots['size'],
			#							toppings=None).calculate_pie_price(self.DB)

			return price
		except KeyError:
			print("Either the pizza or the modality is undefined...")

	def execute(self, inputStr):
		# apply the NLU component
		self.NLU.parse(inputStr)
		self.trackState()

		# and decide what to do next
		newDialogAct = self.selectDialogAct()
		newDialogAct.change = self.DialogFrame.change
		newDialogAct.informedLast = self.DialogFrame.informedLast

		# update semantic frame based on user's request type
		# this has to happen after the dialog act is selected
		if self.NLU.SemanticFrame.Slots["request"] == "cancel":
			self.NLU.SemanticFrame.Slots = defaultdict(lambda:None)
		elif self.NLU.SemanticFrame.Slots["request"] == "start over":
			self.NLU.SemanticFrame.Slots = defaultdict(lambda:None)
		elif self.NLU.SemanticFrame.Slots["request"] == "repeat":
			self.NLU.SemanticFrame.Slots["request"] = None
		elif self.NLU.SemanticFrame.Slots["request"] == "status" and \
								self.NLU.SemanticFrame.Slots['name']:
			self.NLU.SemanticFrame.Slots["request"] = None
		if self.NLU.SemanticFrame.Slots['update_modality'] and \
					self.DialogFrame.previousOrder:
			del self.NLU.SemanticFrame.Slots['update_modality']
			self.DialogFrame.previousOrder = None

		# then generate some meaningful response
		response = self.NLG.generate(newDialogAct)

		# update the slots
		self.PreviousSlots = defaultdict(lambda:None,self.NLU.SemanticFrame.Slots)
		
		return response

	def trackState(self):
		# deny ask for additional pizza
		if self.lastDialogAct and self.lastDialogAct.slot == "anything_else":
			if self.NLU.SemanticFrame.Intent == DialogActTypes.DENY:
				self.NLU.SemanticFrame.Slots['done_ordering'] = True
			else:
				self.NLU.SemanticFrame.Slots['ground_pizza'] = False

		# confirm ask for additional pizza
		# if self.NLU.SemanticFrame.Intent == DialogActTypes.CONFIRM and \
		# 							self.lastDialogAct.slot == "anything_else":
		# 	# self.NLU.clearPizza()
		# 	pass

		if not self.NLU.SemanticFrame.Slots['pizza_type'] and (self.NLU.SemanticFrame.Slots['toppings']):
			self.NLU.SemanticFrame.Slots['pizza_type'] = 'basic'

		# confirm pizza
		if self.NLU.SemanticFrame.Intent == DialogActTypes.CONFIRM and \
									type(self.lastDialogAct.slot)==tuple \
									and self.lastDialogAct.slot[0]==0:

			if self.NLU.SemanticFrame.Slots['revise_preferred']:
				self.DialogFrame.done_with_revision = True
				self.DB.updatePreferred(self.NLU.SemanticFrame.Slots['name'],
									self.NLU.SemanticFrame.Slots['pizza_type'],
									self.NLU.SemanticFrame.Slots['crust'],
									self.NLU.SemanticFrame.Slots['size'],
									self.NLU.SemanticFrame.Slots['toppings'])
				del self.NLU.SemanticFrame.Slots['revise_preferred']


			else:
				self.pizzas.append(Pizza(
					self.NLU.SemanticFrame.Slots['pizza_type'],
					self.NLU.SemanticFrame.Slots['crust'],
					self.NLU.SemanticFrame.Slots['size'],
					self.NLU.SemanticFrame.Slots['toppings'],
					self.NLU.SemanticFrame.Slots['no toppings']))
				self.NLU.clearPizza()
				self.NLU.SemanticFrame.Slots['ground_pizza'] = True

		# confirm order 
		if self.NLU.SemanticFrame.Intent == DialogActTypes.CONFIRM and \
									type(self.lastDialogAct.slot)==tuple \
									and self.lastDialogAct.slot[0]==1:

			#print("(tracking state for confirming an order)")
			self.NLU.SemanticFrame.Slots['ground_order'] = True
			self.cost = self.calculate_price()
			self.DB.save_new_order(self.NLU.SemanticFrame.Slots,
								   self.cost)

		# try to update the order with the preferred pizzas
		if self.NLU.SemanticFrame.Slots['preferred']:
			try:
				preferred_pizza = self.DB.get_preferred(self.NLU.SemanticFrame.Slots['name'])
				for attribute in ['size','crust','pizza_type']:
					self.NLU.SemanticFrame.Slots[attribute] = preferred_pizza[attribute]
				del self.NLU.SemanticFrame.Slots['preferred']
			except Exception:
				pass
			self.DialogFrame.change = False
		
		if self.NLU.SemanticFrame.Slots['update_modality']:
			if self.NLU.SemanticFrame.Slots['name']:
				self.DialogFrame.previousOrder = self.DB.update_modality(self.NLU.SemanticFrame.Slots['name'])

		# if we've just asked to revise the preferred order
		# we should clear the board of pizza information
		if self.NLU.SemanticFrame.Slots['need_to_clear']:

			self.NLU.SemanticFrame.clearPizza()
			del self.NLU.SemanticFrame.Slots['need_to_clear']

		# update the DialogFrame based on the SemanticFrame
		slots_for_dialog_tracking = [self.NLU.SemanticFrame.Slots[s] for s in 
													['ground_pizza','ground_order', 'request']]
		slots_filled = set([s for s in 
							['pizza_type','crust','size','name','address','number','modality'] if 
							self.NLU.SemanticFrame.Slots[s]])
		
		# logic for making better sounding NLG by grounding by acknowledgement turn-initially
		if self.NLU.SemanticFrame.Intent == DialogActTypes.INFORM:
			if slots_filled == self.DialogFrame.slots_filled and len(slots_filled) > 0:
				# we didn't add any new slots and we didn't do any non-inform operations
				self.DialogFrame.change = True
				self.DialogFrame.informedLast = True
			else:
				# we added a slot with new information
				self.DialogFrame.change = False
				self.DialogFrame.informedLast = True
		else:
			self.DialogFrame.change = False
			self.DialogFrame.informedLast = False
		
		# fill in dialog frame info, and propagate user info from DB
		self.DialogFrame.update(*slots_for_dialog_tracking,slots_filled)
		self.consolidate_user_data()

		# fill in the order status
		if self.NLU.SemanticFrame.Slots['request'] == 'status' and \
								self.NLU.SemanticFrame.Slots['name']:
			# look it up the in db
			# just look up their most recent order
			self.NLU.SemanticFrame.Slots['order_status'] = self.DB.get_order_status(self.NLU.SemanticFrame.Slots['name'])

	def selectDialogAct(self):
		dialogAct = DialogAct()
		# by default, return a Hello dialog act
		dialogAct.DialogActType = DialogActTypes.HELLO

		# Universals
		if self.DialogFrame.request == "cancel":
			dialogAct.DialogActType = DialogActTypes.GOODBYE

		elif self.DialogFrame.request == "repeat" or self.NLU.SemanticFrame.Intent == DialogActTypes.UNDEFINED:
			if self.lastDialogAct:
				dialogAct = self.lastDialogAct
			else:
				dialogAct.DialogActType = DialogActTypes.HELLO

		elif self.DialogFrame.request == "start over":
			dialogAct.DialogActType = DialogActTypes.HELLO

		elif self.DialogFrame.request == "status":
			if self.NLU.SemanticFrame.Slots['name']:
				dialogAct.DialogActType = DialogActTypes.INFORM
				dialogAct.slot = (2,self.NLU.SemanticFrame.Slots)
			else:
				dialogAct.DialogActType = DialogActTypes.REQUEST
				dialogAct.slot = 'name'
		elif self.NLU.SemanticFrame.Intent == DialogActTypes.DENY and self.lastDialogAct.slot != "anything_else":
			dialogAct.DialogActType = DialogActTypes.REQALTS
			dialogAct.slot = 'wildcard'	

		# if non-optional (non-toppings) information not added, we should revise
		elif not self.information_added() and self.NLU.SemanticFrame.Intent == DialogActTypes.INFORM:
			# we need to reqalts
			dialogAct.DialogActType = DialogActTypes.REQALTS
			dialogAct.slot = self.lastDialogAct.slot

		# try to update to the preferred
		elif self.NLU.SemanticFrame.Slots['preferred'] and not \
					self.NLU.SemanticFrame.Slots['name']:
			dialogAct.DialogActType = DialogActTypes.REQUEST
			dialogAct.slot = 'name'
		# try to fill out modality switch if they want t
		elif self.NLU.SemanticFrame.Slots['update_modality']:
			if not self.NLU.SemanticFrame.Slots['name']:
				dialogAct.DialogActType = DialogActTypes.REQUEST
				dialogAct.slot = 'name'
			else:
				dialogAct.DialogActType = DialogActTypes.INFORM
				dialogAct.slot = self.DialogFrame.previousOrder
		# try to modify the preferred
		elif self.NLU.SemanticFrame.Slots['revise_preferred'] and not \
					self.NLU.SemanticFrame.Slots['name']:
			dialogAct.DialogActType = DialogActTypes.REQUEST
			dialogAct.slot = 'name'
		elif self.DialogFrame.done_with_revision:
			dialogAct.DialogActType = DialogActTypes.INFORM
			dialogAct.slot = 'revise_preferred'
			self.DialogFrame.done_with_revision = False

		# Order has been grounded; return goodbye dialog act
		elif self.DialogFrame.ground_order == True:
			dialogAct.DialogActType = DialogActTypes.GOODBYE
			dialogAct.complete = True
			dialogAct.slot = self.cost

		# Pizza grounded, order not grounded
		elif self.DialogFrame.ground_pizza == True:

			# Not done ordering more pizzas
			if not self.NLU.SemanticFrame.Slots['done_ordering']:
				dialogAct.DialogActType = DialogActTypes.REQUEST
				dialogAct.slot = "anything_else"

			# Get user if needed
			elif not self.NLU.SemanticFrame.Slots['name']:
				dialogAct.DialogActType = DialogActTypes.REQUEST
				dialogAct.slot = "name"

			# Get modality if needed
			elif not self.NLU.SemanticFrame.Slots['modality']:
				dialogAct.DialogActType = DialogActTypes.REQUEST
				dialogAct.slot = "modality"

			# Get address if needed
			elif self.NLU.SemanticFrame.Slots['modality'] == "delivery" and not \
										self.NLU.SemanticFrame.Slots['address']:
				dialogAct.DialogActType = DialogActTypes.REQUEST
				dialogAct.slot = "address"
		
			# Ground Order
			else:
				dialogAct.DialogActType = DialogActTypes.REQUEST
				#dialogAct.slot = (1,self.NLU.SemanticFrame.Slots)
				dialogAct.slot = (1,self.NLU.SemanticFrame.Slots,self.pizzas)
	
		# Pizza not yet grounded
		else:
			# Get pizza type if needed
			if not self.NLU.SemanticFrame.Slots['pizza_type']:
				dialogAct.DialogActType = DialogActTypes.REQUEST
				dialogAct.slot = "pizza_type"

			# Get crust if needed
			elif not self.NLU.SemanticFrame.Slots['crust']:
				dialogAct.DialogActType = DialogActTypes.REQUEST
				dialogAct.slot = "crust"

			# Get size if needed
			elif not self.NLU.SemanticFrame.Slots['size']:
				dialogAct.DialogActType = DialogActTypes.REQUEST
				dialogAct.slot = "size"

			# Ground Pizza
			else:
				dialogAct.DialogActType = DialogActTypes.REQUEST
				# create a temporary pizza from the slots so that we can update the toppings
				temporary_pizza = Pizza(pizza_type=self.NLU.SemanticFrame.Slots['pizza_type'],
										crust=self.NLU.SemanticFrame.Slots['crust'],
										size=self.NLU.SemanticFrame.Slots['size'],
										toppings=self.NLU.SemanticFrame.Slots['toppings'],
										no_toppings=self.NLU.SemanticFrame.Slots['no toppings'])
				temporary_pizza.populate_toppings()
				dialogAct.slot = (0,temporary_pizza)

		self.lastDialogAct = dialogAct
		return dialogAct

	def information_added(self):
		# in addition to the logic below, to accomodate toppings addition we should check
		# for toppings updates here as well.

		without_toppings_current = defaultdict(
							lambda:None,self.NLU.SemanticFrame.Slots)
		if 'toppings' in without_toppings_current.keys():
			without_toppings_current['toppings']
		without_toppings_past = defaultdict(lambda:None,self.PreviousSlots)
		if 'toppings' in without_toppings_past.keys():
			del without_toppings_past['toppings']
		for k,v in without_toppings_current.items():
			if without_toppings_past[k]!=v or k not in without_toppings_past.keys():
				return True
		if set(without_toppings_current.values())=={None}:
			return True
		else:
			return False

	def consolidate_user_data(self):
		# look up data from the DB to try and populate slots about the user automatically
		user_data = [None]*3
		attributes = ['name','address','number']
		for i,attribute in enumerate(attributes):
			user_data[i] = self.NLU.SemanticFrame.Slots[attribute]
		try:
			indexer,value = next((attributes[i],a) for i,a in enumerate(user_data) if a)
			# if there is a missing value we can fill of the users' data
			if None in user_data and len(user_data)!=user_data.count(None):
				# figure out what portion we know
				match = self.DB.users[self.DB.users[indexer].eq(value)]
				for attribute in attributes:
					# use the DB to populate the semantic frame
					self.NLU.SemanticFrame.Slots[attribute] = match[attribute].values[0]
		except StopIteration:
			pass

