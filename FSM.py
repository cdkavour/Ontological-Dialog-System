from DialogActTypes import DialogActTypes
from DialogAct import DialogAct
from collections import defaultdict

# 0 greet > 1 pizza type > 2 crust >  3 size 
# > 4 ground_pizza > 5 name > 6 phone number 
# > 7 modality > 8 if_delivery(address) > 9 ground_all > goodbye

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
		self.NLU.SemanticFrame = self.NLU.parse(inputStr)
		if self.NLU.SemanticFrame.Intent == DialogActTypes(5):
			# cancel repeat or start over
			if self.NLU.SemanticFrame.Slots['request'] == 'cancel':
				# just leave
				self.state = 9
				outstr = self.NLG.generate(DialogAct(DialogActTypes.GOODBYE,None))
			elif self.NLU.SemanticFrame.Slots['request']== 'repeat':
				# repeat the last thing, don't advance the state 
				outstr = self.NLG.generate(DialogAct(DialogActTypes.REQUEST,self.slot_to_fill[self.state]))
			elif self.NLU.SemanticFrame.Slots['request']=='start over':
				self.state = 1
				self.NLU.SemanticFrame.Slots = defaultdict(lambda:None)
				outstr = self.NLG.generate(DialogAct(DialogActTypes.REQUEST,'pizza_type'))
		elif self.state == 0:
			self.state +=1
			outstr = self.NLG.generate(DialogAct(DialogActTypes.REQUEST,self.slot_to_fill[self.state]))
		elif self.state == 3 or self.state == 8:
			if self.NLU.SemanticFrame.Intent == DialogActTypes(4):
				if self.NLU.SemanticFrame.Slots[self.slot_to_fill[self.state]]:
					self.state += 1
					outstr = self.NLG.generate(DialogAct(DialogActTypes.REQUEST,(1*(self.state-9)//5+1,self.NLU.SemanticFrame.Slots)))
				else:
					# the slot did not get filled, try again
					outstr = self.NLG.generate(DialogAct(DialogActTypes.REQALTS,self.slot_to_fill[self.state]))

			# otherwise I don't know what to do
			else:
				outstr = self.NLG.generate(DialogAct(DialogActTypes.REQALTS,self.slot_to_fill[self.state]))

		elif self.state == 4:
			# ground
			if self.NLU.SemanticFrame.Intent == DialogActTypes(7):
				# we got right, proceed
				self.state +=1
				outstr = self.NLG.generate(DialogAct(DialogActTypes.REQUEST,self.slot_to_fill[self.state]))
			elif self.NLU.SemanticFrame.Intent == DialogActTypes(8):
				# we got wrong, just start over
				self.state = 1
				self.NLU.Slots = defaultdict(lambda:None)
				outstr = self.NLG.generate(DialogAct(DialogActTypes.REQALTS,'pizza_type'))
			else:
				# we got an unexpected answer, try again
				outstr = self.NLG.generate(DialogAct(DialogActTypes.REQALTS,(0,self.NLU.SemanticFrame.Slots)))
		elif self.state == 9:
			# ground
			if self.NLU.SemanticFrame.Intent == DialogActTypes(7):
				# we got right, proceed
				self.state +=1
				outstr = self.NLG.generate(DialogAct(DialogActTypes.GOODBYE,None))
			elif self.NLU.SemanticFrame.Intent == DialogActTypes(8):
				# we got wrong
				# if we got here, assume the pizza was right
				# so go back to state 5 which is the first thing
				self.state = 5
				outstr = self.NLG.generate(DialogAct(DialogActTypes.REQALTS,'name'))
			else:
				# we got an unexpected answer, try again
				outstr = self.NLG.generate(DialogAct(DialogActTypes.REQALTS,(1,self.NLU.SemanticFrame.Slots)))
		else: # the "normal states"
			# they provide the right information
			if self.NLU.SemanticFrame.Intent == DialogActTypes(4):
				relevant_slot = self.NLU.SemanticFrame.Slots[self.slot_to_fill[self.state]]
				if relevant_slot:		
					self.state += 1
					if relevant_slot == 'pick-up':
						self.state +=1
						outstr = self.NLG.generate(DialogAct(DialogActTypes.REQUEST,(1,self.NLU.SemanticFrame.Slots)))
					else:
						outstr = self.NLG.generate(DialogAct(DialogActTypes.REQUEST,self.slot_to_fill[self.state]))
				else:
					# the slot did not get filled, try again
					outstr = self.NLG.generate(DialogAct(DialogActTypes.REQALTS,self.slot_to_fill[self.state]))

			# otherwise I don't know what to do
			else:
				outstr = self.NLG.generate(DialogAct(DialogActTypes.REQALTS,self.slot_to_fill[self.state]))
		return outstr