class DialogFrameSimple:

	def __init__(self):
		self.FrameName = "DialogFrameSimple"
		self.ground_pizza = False
		self.ground_order = False
		self.request = None
		self.order_status = None
		self.slots_filled = set()
		self.change = None
		self.informedLast = None

	def update(self,ground_pizza,ground_order,request,slots):
		self.ground_pizza = False if not ground_pizza else True
		self.ground_order = False if not ground_order else True
		self.request = request
		self.slots_filled = self.slots_filled.union(slots)