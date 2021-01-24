from DialogActTypes import DialogActTypes
from DialogAct import DialogAct
import pdb

# 0 greet >
# 1 pizza type 
# 2 crust
# 3 size
# 4 ground_pizza 
# 5 name 
# 6 phone number 
# 7 pickup or delivery 
# 8 if_delivery(address)
# 9 ground_all > goodbye

# UNDEFINED = 1	HELLO = 2	GOODBYE = 3	INFORM = 4
# REQUEST = 5	REQALTS = 6	CONFIRM = 7	DENY = 8

class FSM:

	def __init__(self, NLU, NLG, universals):
		# add whatever you want here
		self.Name = "FSM DM"
		self.state = 0
		self.NLU = NLU
		self.NLG = NLG
		self.slot_to_fill = [None,'pizza_type','crust','size','pizza','name','number','modality','address','order',None]
		self.universals = universals

	def execute(self, inputStr):
		nlu_output = self.NLU.parse(inputStr)
		try:
			nlu_output.Intent = DialogActTypes[nlu_output.Intent]
		except KeyError:
			pass 
		print(self.state,nlu_output.Intent,nlu_output.Slots,sep='\t')
		if self.universals and nlu_output.Intent == DialogActTypes(5):
			# cancel repeat or start over
			if nlu_output.Slots['request'] == 'cancel':
				# just leave
				self.state = 9
			elif nlu_output.Slots['request']== 'repeat':
				# repeat the last thing, don't advance the state 
				# TODO should this be a reqalt or request?
				outstr = self.NLG.generate(DialogAct(da_type=6,
											slot=self.slot_to_fill[self.state]))
			elif nlu.output.Slots['reqeust'=='start_over']:
				self.state = 0
				self.NLU.Slots = {}
				outstr = self.NLG.generate(DialogAct(da_type=6,slot='pizza_type'))
		elif self.state == 0:
			outstr = self.NLG.generate(DialogAct(da_type=2))
			self.state +=1
			print(self.state)
		elif self.state == 4:
			# ground
			if nlu_output.Intent == DialogActTypes(7):
				# we got right, proceed
				self.state +=1
				outstr = self.NLG.generate(DialogAct(da_type=5,
								  slot=self.slot_to_fill[self.state]))
			elif nlu_output.Intent == DialogActTypes(8):
				# we got wrong, just start over
				self.state = 0
				self.NLU.Slots = {}
				outstr = self.NLG.generate(DialogAct(da_type=6,slot='pizza_type'))
			else:
				# we got an unexpected answer, try again
				outstr = self.NLG.generate(DialogAct(da_type=6,
											slot=self.slot_to_fill[self.state]))
		elif self.state == 9:
			# ground
			if nlu_output.Intent == DialogActTypes(7):
				# we got right, proceed
				self.state +=1
				outstr = self.NLG.generate(DialogAct(da_type=3))
			elif nlu_output.Intent == DialogActTypes(8):
				# we got wrong
				# if we got here, assume the pizza was right
				# so go back to state 5 which is the first thing
				self.state = 5
				outstr = self.NLG.generate(DialogAct(da_type=6,slot='name'))
			else:
				# we got an unexpected answer, try again
				outstr = self.NLG.generate(DialogAct(da_type=6,
											slot=self.slot_to_fill[self.state]))
		else: # the "normal states"
			# they provide the right information
			if nlu_output.Intent == DialogActTypes(4):
				try:
					
					relevant_slot = nlu_output.Slots[self.slot_to_fill[self.state]]
					if relevant_slot == 'pickup':
						# special case for address bypassed for pickup
						self.state +=1
					self.state += 1
					outstr = self.NLG.generate(DialogAct(da_type=5,
												slot=self.slot_to_fill[self.state]))
				except KeyError:
					# the slot did not get filled, try again
					outstr = self.NLG.generate(DialogAct(da_type=6,
												slot=self.slot_to_fill[self.state]))

			# otherwise I don't know what to do
			else:
				outstr = self.NLG.generate(DialogAct(da_type=6,
											slot=self.slot_to_fill[self.state]))
		print(self.state)
		return outstr