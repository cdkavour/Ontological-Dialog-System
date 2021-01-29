from DialogFrameSimple import DialogFrameSimple
from DialogAct import DialogAct
from DialogActTypes import DialogActTypes
from collections import defaultdict
import math,random,json,pandas as pd

class Pizza:
	def __init__(self,specialty_type=None,crust=None,size=None,toppings=None):
		self.type = specialty_type
		self.crust = crust
		self.size = size
		self.toppings = toppings if toppings else set()
		self.price = None

	def _populate_toppings(self):
		if self.type:
			toppings_map = {'hawaiian': {'pineapple','ham','mozzarella'},
						'meat lovers':{'mozzarella','pepperoni','ham','bacon','sausage'},
						'4 cheese':{'mozzarella','cheddar','swiss','provelone'},
						'pepperoni':{'mozzarella','pepperoni'},
						'veggie supreme':{'mozzarella','green peppers','red onions','mushrooms','black olives'},
						'vegan':{'green peppers','red onions','mushrooms','black olives'}}
			self.toppings = self.toppings.union(toppings_map[self.type])

	def calculate_pie_price(self,DB):
		# compute price based on specialty, size, and crust
		self._populate_toppings()
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
		self.open_orders = pd.DataFrame(self.data['open_orders'])
		self.crusts = pd.DataFrame(self.data['crusts'])
		self.modality = self.data['modality'][0]
		self.order_idx = self.data['order_idx']

	def save_new_order(self,slots,cost):
		num_digits = 5-int(math.log10(self.order_idx))+1
		confirmation_number = '0'*num_digits+str(self.order_idx)
		self.data['open_orders'].append({'name':slots['user'],
							'confirmation_number':confirmation_number,
							'modality':slots['modality'],
							'address':slots['address'], # this could be none, that's okay
							'status':'processing',
							'cost':cost})
		self.data['order_idx'] +=1
		with open(self.path,'w') as f:
			json.dump(self.data,f,indent=3)

class FrameDMSimple:

	def __init__(self, NLU, NLG):
		self.NLU = NLU
		# define frame below, for example:
		self.PreviousSlots = defaultdict(lambda:None)
		self.DialogFrame = DialogFrameSimple()
		self.DB = DB('db.json')
		self.NLG = NLG
		self.NLU.setDB(self.DB)
		self.lastDialogAct = None

	def calculate_price(self):
		try:
			base_price = self.DB.modality[self.NLU.SemanticFrame.Slots['modality']]
			price = base_price + Pizza(specialty_type=self.NLU.SemanticFrame.Slots['pizza_type'],
										crust=self.NLU.SemanticFrame.Slots['crust'],
										size=self.NLU.SemanticFrame.Slots['size'],
										toppings=None).calculate_pie_price(self.DB)
			return price
		except KeyError:
			print("Either the pizza or the modality is undefined...")

	def execute(self, inputStr):
		# apply the NLU component
		self.NLU.parse(inputStr)
		
		# update the dialog frame with the new information
		# return out if something got modified from an original value
		self.trackState()

		# and decide what to do next
		newDialogAct = self.selectDialogAct()
		newDialogAct.change = self.DialogFrame.change
		newDialogAct.informedLast = self.DialogFrame.informedLast

		# update semantic frame based on user's request type
		# this has to happen after the dialog act is selected
		if self.NLU.SemanticFrame.Slots["request"] == "cancel":
			self.NLU.SemanticFrame.Slots = defaultdict(lambda:None)
			self.NLU.SemanticFrame.order = []
		elif self.NLU.SemanticFrame.Slots["request"] == "start over":
			self.NLU.SemanticFrame.Slots = defaultdict(lambda:None)
			self.NLU.SemanticFrame.order = []
		elif self.NLU.SemanticFrame.Slots["request"] == "repeat":
			self.NLU.SemanticFrame.Slots["request"] = None
		elif self.NLU.SemanticFrame.Slots["request"] == "status" and \
								self.NLU.SemanticFrame.Slots['name']:
			self.NLU.SemanticFrame.Slots["request"] = None

		# then generate some meaningful response
		response = self.NLG.generate(newDialogAct)

		# update the slots
		self.PreviousSlots = defaultdict(lambda:None,self.NLU.SemanticFrame.Slots)
		
		return response

	def trackState(self):

		# confirm pizza
		if self.NLU.SemanticFrame.Intent == DialogActTypes.CONFIRM and \
									type(self.lastDialogAct.slot)==tuple \
									and self.lastDialogAct.slot[0]==0:
			self.NLU.SemanticFrame.Slots['ground_pizza'] = True
		# confirm order 
		if self.NLU.SemanticFrame.Intent == DialogActTypes.CONFIRM and \
									type(self.lastDialogAct.slot)==tuple \
									and self.lastDialogAct.slot[0]==1:
			self.NLU.SemanticFrame.Slots['ground_order'] = True
			self.cost = self.calculate_price()
			self.DB.save_new_order(self.NLU.SemanticFrame.Slots,
								   self.cost)

		# try to update the order with the preferred pizzas
		if self.NLU.SemanticFrame.Slots['preferred']:
			try:
				preferred_pizza = self.DB.users.loc[self.DB.users.name == \
									self.NLU.SemanticFrame.Slots['name']].preferred.values[0]
				for attribute in ['size','crust','pizza_type']:
					self.NLU.SemanticFrame.Slots[attribute] = preferred_pizza[attribute]
				del self.NLU.SemanticFrame.Slots['preferred']

			except Exception:
				pass
			self.DialogFrame.change = False

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
			# for now, just look up their most recent order
			self.NLU.SemanticFrame.Slots['order_status'] = self.DB.open_orders[self.DB.open_orders.name.eq(self.NLU.SemanticFrame.Slots['name'])].status.values[-1]

	def selectDialogAct(self):
		dialogAct = DialogAct()
		import pdb;pdb.set_trace()
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
		elif self.NLU.SemanticFrame.Intent == DialogActTypes.DENY:
			dialogAct.DialogActType = DialogActTypes.REQALTS
			dialogAct.slot = 'wildcard'

		# toppings not handled, but have to be ignored to get around counting
		elif not self.information_added() and self.NLU.SemanticFrame.Intent == DialogActTypes.INFORM:
			# we need to reqalts
			dialogAct.DialogActType = DialogActTypes.REQALTS
			dialogAct.slot = self.lastDialogAct.slot

		# try to update to the preferred
		elif self.NLU.SemanticFrame.Slots['preferred'] and not \
							self.NLU.SemanticFrame.Slots['name']:
			dialogAct.DialogActType = DialogActTypes.REQUEST
			dialogAct.slot = 'name'

		# Order has been grounded; return goodbye diolog act
		elif self.DialogFrame.ground_order == True:
			dialogAct.DialogActType = DialogActTypes.GOODBYE
			dialogAct.complete = True
			dialogAct.slot = self.cost

		# Pizza grounded, order not grounded
		elif self.DialogFrame.ground_pizza == True:

			# Get user if needed
			if not self.NLU.SemanticFrame.Slots['name']:
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
				dialogAct.slot = (1,self.NLU.SemanticFrame.Slots)
	
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
				dialogAct.slot = (0,self.NLU.SemanticFrame.Slots)

		self.lastDialogAct = dialogAct
		return dialogAct

	def information_added(self):
		without_toppings_current = defaultdict(
							lambda:None,self.NLU.SemanticFrame.Slots)
		if 'toppings' in without_toppings_current.keys():
			without_toppings_current['toppings']
		without_toppings_past = defaultdict(lambda:None,self.PreviousSlots)
		if 'toppings' in without_toppings_past.keys():
			del without_toppings_past['toppings']
		for k,v in without_toppings_current.items():
			if without_toppings_past[k]!=v:
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

