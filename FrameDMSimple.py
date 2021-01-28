from DialogFrameSimple import DialogFrameSimple
from DialogAct import DialogAct
from DialogActTypes import DialogActTypes
from collections import defaultdict
import math,random,json,pdb,pandas as pd


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

	def save_new_order(self,user,modality,address,cost):
		num_digits = 5-int(math.log10(self.order_idx))+1
		confirmation_number = '0'*num_digits+str(self.order_idx)
		self.data['open_orders'].append({'name':user,
							'confirmation_number':confirmation_number,
							'modality':modality,
							'address':address, # this could be none, that's okay
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
		self.currentSemanticFrame = None

	def calculate_price(self):
		try:
			base_price = self.DB.modality[self.currentSemanticFrame.Slots['modality']]
			price = base_price + self.currentSemanticFrame.order[0].calculate_pie_price(self.DB)
			return price
		except KeyError:
			print("Either the pizza or the modality is undefined...")

	def execute(self, inputStr):
		# apply the NLU component
		self.currentSemanticFrame = self.NLU.parse(inputStr)
		pdb.set_trace()
		# update the dialog frame with the new information
		# return out if something got modified from an original value
		change = self.trackState()

		# and decide what to do next
		newDialogAct = self.selectDialogAct()
		newDialogAct.change = change

		# update semantic frame based on user's request type
		if self.currentSemanticFrame.Slots["request"] == "cancel":
			self.currentSemanticFrame.Slots = defaultdict(lambda:None)
			self.currentSemanticFrame.order = []
		elif self.currentSemanticFrame.Slots["request"] == "start over":
			self.currentSemanticFrame.Slots = defaultdict(lambda:None)
			self.currentSemanticFrame.order = []
		elif self.currentSemanticFrame.Slots["request"] == "repeat":
			self.currentSemanticFrame.Slots["request"] = None
		elif self.currentSemanticFrame.Slots["request"] == "status" and \
								self.currentSemanticFrame.Slots['name']:
			self.currentSemanticFrame.Slots["request"] = None

		# then generate some meaningful response
		response = self.NLG.generate(newDialogAct)
		if self.lastDialogAct.complete:
			cost = self.calculate_price()
			self.DB.save_new_order(self.currentSemanticFrame.Slots['name'],
								   self.currentSemanticFrame.Slots['modality'],
								   self.currentSemanticFrame.Slots['address'],
								   cost)

		self.PreviousSlots = defaultdict(lambda:None,self.currentSemanticFrame.Slots)
		return response

	def trackState(self):
		# Confirm or deny pizza
		if self.currentSemanticFrame.Intent == DialogActTypes.CONFIRM and \
									type(self.lastDialogAct.slot)==tuple \
									and self.lastDialogAct.slot[0]==0:
			self.currentSemanticFrame.Slots['ground_pizza'] = True
			self.currentSemanticFrame.make_pizza()
		elif self.currentSemanticFrame.Intent == DialogActTypes.DENY and \
									type(self.lastDialogAct.slot)==tuple \
									and self.lastDialogAct.slot[0]==0:
			self.currentSemanticFrame.Slots['pizza_type'] = None
			self.currentSemanticFrame.Slots['crust'] = None
			self.currentSemanticFrame.Slots['size'] = None
		# Confirm or deny order
		if self.currentSemanticFrame.Intent == DialogActTypes.CONFIRM and \
									type(self.lastDialogAct.slot)==tuple \
									and self.lastDialogAct.slot[0]==1:
			self.currentSemanticFrame.Slots['ground_order'] = True
		elif self.currentSemanticFrame.Intent == DialogActTypes.DENY and \
									type(self.lastDialogAct.slot)==tuple \
									and self.lastDialogAct.slot[0]==1:
			self.currentSemanticFrame.Slots['name'] = None
			self.currentSemanticFrame.Slots['number'] = None
			self.currentSemanticFrame.Slots['modality'] = None
			self.currentSemanticFrame.Slots['address'] = None
			change = True
		if self.currentSemanticFrame.Slots['preferred']:
			try:
				preferred_pizza = self.DB.users.loc[self.DB.users.name == \
									self.currentSemanticFrame.Slots['name']].preferred.values[0]
				for attribute in ['size','crust','pizza_type']:
					self.currentSemanticFrame.Slots[attribute] = preferred_pizza[attribute]
			except Exception:
				pass
			change = False
		slots_for_dialog_tracking = [self.currentSemanticFrame.Slots[s] for s in 
													['ground_pizza','ground_order', 'request']]
		slots_filled = set([s for s in 
							['pizza_type','crust','size','name','address','modality'] if 
							self.currentSemanticFrame.Slots[s]])
		if self.currentSemanticFrame.Intent == DialogActTypes.INFORM and slots_filled == self.DialogFrame.slots_filled and len(slots_filled) > 0:
			# we didn't add any new slots and we didn't do any non-inform operations
			change = True
		else:
			change = False

		# fill in dialog frame info, and propagate user info from DB
		self.DialogFrame.update(*slots_for_dialog_tracking,slots_filled)
		self.consolidate_user_data()

		# fill in the order status
		if self.currentSemanticFrame.Slots['request'] == 'status' and \
								self.currentSemanticFrame.Slots['name']:
			# look it up the in db
			# for now, just look up their most recent order
			self.currentSemanticFrame.Slots['order_status'] = self.DB.open_orders[self.DB.open_orders.name.eq(self.currentSemanticFrame.Slots['name'])].status.values[-1]

		return change

	def selectDialogAct(self):
		dialogAct = DialogAct()

		# by default, return a Hello dialog act
		dialogAct.DialogActType = DialogActTypes.HELLO

		# Universals
		if self.DialogFrame.request == "cancel":
			dialogAct.DialogActType = DialogActTypes.GOODBYE

		elif self.DialogFrame.request == "repeat":
			dialogAct.DialogActType = DialogActTypes.REQALTS
			dialogAct.slot = self.lastDialogAct.slot

		elif self.DialogFrame.request == "start over":
			dialogAct.DialogActType = DialogActTypes.HELLO

		elif self.DialogFrame.request == "status":
			print('heres')
			dialogAct.DialogActTypes = DialogActTypes.INFORM
			dialogAct.slot = (2,self.currentSemanticFrame.Slots)

		# toppings not handled, but have to be ignored to get around counting
		elif not self.information_added():
			# we need to reqalts
			dialogAct.DialogActType = DialogActTypes.REQALTS
			dialogAct.slot = self.lastDialogAct.slot

		# try to update to the preferred
		elif self.currentSemanticFrame.Slots['preferred'] and not \
							self.currentSemanticFrame.Slots['name']:
			dialogAct.DialogActType = DialogActTypes.REQUEST
			dialogAct.slot = 'name'

		# Order has been grounded; return goodbye diolog act
		elif self.DialogFrame.ground_order == True:
			dialogAct.DialogActType = DialogActTypes.GOODBYE
			dialogAct.complete = True

		# Pizza grounded, order not grounded
		elif self.DialogFrame.ground_pizza == True:

			# Get user if needed
			if not self.currentSemanticFrame.Slots['name']:
				dialogAct.DialogActType = DialogActTypes.REQUEST
				dialogAct.slot = "name"

			# Get modality if needed
			elif not self.currentSemanticFrame.Slots['modality']:
				dialogAct.DialogActType = DialogActTypes.REQUEST
				dialogAct.slot = "modality"

			# Get address if needed
			elif self.currentSemanticFrame.Slots['modality'] == "delivery" and not \
										self.currentSemanticFrame.Slots['address']:
				dialogAct.DialogActType = DialogActTypes.REQUEST
				dialogAct.slot = "address"
		
			# Ground Order
			else:
				dialogAct.DialogActType = DialogActTypes.REQUEST
				dialogAct.slot = (1,self.currentSemanticFrame.Slots)
	
		# Pizza not yet grounded
		else:

			# Get pizza type if needed
			if not self.currentSemanticFrame.Slots['pizza_type']:
				dialogAct.DialogActType = DialogActTypes.REQUEST
				dialogAct.slot = "pizza_type"

			# Get crust if needed
			elif not self.currentSemanticFrame.Slots['crust']:
				dialogAct.DialogActType = DialogActTypes.REQUEST
				dialogAct.slot = "crust"

			# Get size if needed
			elif not self.currentSemanticFrame.Slots['size']:
				dialogAct.DialogActType = DialogActTypes.REQUEST
				dialogAct.slot = "size"

			# Ground Pizza
			else:
				dialogAct.DialogActType = DialogActTypes.REQUEST
				dialogAct.slot = (0,self.currentSemanticFrame.Slots)

		self.lastDialogAct = dialogAct
		return dialogAct

	def information_added(self):
		without_toppings_current = defaultdict(
							lambda:None,self.currentSemanticFrame.Slots)
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
		user_data = [None]*3
		attributes = ['name','address','number']
		for i,attribute in enumerate(attributes):
			user_data[i] = self.currentSemanticFrame.Slots[attribute]
		try:
			indexer,value = next((attributes[i],a) for i,a in enumerate(user_data) if a)
			# if there is a missing value we can fill of the users' data
			if None in user_data and len(user_data)!=user_data.count(None):
				# figure out what portion we know
				match = self.DB.users[self.DB.users[indexer].eq(value)]
				for attribute in attributes:
					# use the DB to populate the semantic frame
					self.currentSemanticFrame.Slots[attribute] = match[attribute].values[0]
		except StopIteration:
			pass

