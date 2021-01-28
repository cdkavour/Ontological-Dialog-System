from collections import defaultdict
import pdb

class SemanticFrame:

	def __init__(self):
		self.Domain = None
		self.Intent = None
		self.Slots = defaultdict(lambda:None)
		self.order = []

	def make_pizza(self):
		self.order.append(Pizza(specialty_type=self.Slots['pizza_type'],
								crust=self.Slots['crust'],
								size=self.Slots['size'],
								toppings=self.Slots['toppings']))
		self.order[-1]._populate_toppings()
		self.Slots['pizza_type']=self.Slots['crust']=self.Slots['size']=None

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
		pdb.set_trace()
		self._populate_toppings()
		# call the ƒice db and calculate
		# the base price is the price of the crust
		price = DB.crusts.loc[DB.crusts['size'].eq(self.size) & DB.crusts.name.eq(self.crust)].price.values[0]
		# add on the price for all toppings
		for topping in self.toppings:
			price += DB.toppings.loc[DB.toppings.name.eq(topping)].price.values[0]
		return price

