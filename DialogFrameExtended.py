class DialogFrameExtended:

	def __init__(self):
		self.FrameName = "DialogFrameExtended"
		self.ground_pizza = False
		self.ground_order = False
		self.request = None
		self.order_status = None
		self.slots_filled = set()
		self.change = None
		self.informedLast = None
		self.pizzas = []

		# whether or not you are trying to update
		# the modality of a previous order
		self.previousOrder = None 

		# whether or nnot you are trying to update the
		# preferred order
		self.done_with_revision = False

	def update(self,ground_pizza,ground_order,request,slots):
		self.ground_pizza = False if not ground_pizza else True
		self.ground_order = False if not ground_order else True
		self.request = request
		self.slots_filled = self.slots_filled.union(slots)