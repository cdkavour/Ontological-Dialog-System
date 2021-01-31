from DialogActTypes import DialogActTypes

class DialogAct:

	def __init__(self,*args):
		if len(args)== 2:
			self.DialogActType = args[0]
			self.slot = args[1]
		else:
			self.DialogActType = DialogActTypes.UNDEFINED
			self.slot = None
			self.change = None
			self.complete = False
			self.informedLast = False