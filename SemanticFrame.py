from collections import defaultdict

class SemanticFrame:

	def __init__(self):
		self.Domain = None
		self.Intent = None
		self.Slots = defaultdict(lambda:None)
		self.order = []

	# def make_pizza(self):
	# 	self.order.append(Pizza(specialty_type=self.Slots['pizza_type'],
	# 							crust=self.Slots['crust'],
	# 							size=self.Slots['size'],
	# 							toppings=self.Slots['toppings']))
	# 	self.order[-1]._populate_toppings()
	# 	# the following line is something of the sort we will need 
	# 	# for ordering multiple pizzas
	# 	# self.Slots['pizza_type']=self.Slots['crust']=self.Slots['size']=None



