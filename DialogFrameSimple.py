import json

class DialogFrameSimple:

    def __init__(self):
        self.FrameName = "DialogFrameSimple"
        # add whatever fields you want here
        # the things that are part of the IS are 
        # pizza type, crust, size, 
        # person (name & number), modality, address
        self.pizza = Pizza()
        self.user = None
        self.modality = None
        self.address = None
        self.price = 0
        self.ground_pizza = False
        self.ground_order = False

    def update(self,slots,DB):
    	self.pizza = Pizza(specialty_type=slots[0],crust=slots[1],size=slots[2])
    	self.user = slots[3]
    	self.modality = slots[4]
    	self.address = slots[5]
    	self.ground_pizza = False if slots[6]==None else True
    	self.ground_order = False if slots[7]==None else True
    	self.consolidate_user_data(DB)

    def consolidate_user_data(self,DB):
    	user_data = [self.user,self.modality,self.address]
    	if None in user_data and len(user_data)!=user_data.count(None):
    		# try and fill in the rest of the information from the DB
    		# use next() function to query

    def ready_to_ground_order(self):
    	if len(self.pizza.empty_slots())==0 and None not in [
    		self.user,self.modality,self.address,self.price]:
    		return True
    	else: 
    		return False

    def ready_to_ground_pizza(self):
    	if len(self.pizza.empty_slots())==0 :
    		return True
    	else:
    		return False

    def calculate_price(self,DB):
    	try:
    		base_price = DB['modality_price'][self.modality]
    		price = base_price + self.pizza._calculate_pie_price(DB)
    		return price
    	except KeyError:
    		print("Either the pizza or the modality is undefined...")

class Pizza:
	def __init__(self,specialty_type=None,crust=None,size=None):
		self.type = specialty_type
		self.crust = crust
		self.size = size
		self.toppings = self._populate_toppings()
		self.price = None
	def set_value(self,value):
		if value in {'thin','regular','deep_dish','gluten_free'}:
			self.crust = value
		elif value in {'small','medium','large'}:
			self.size = value
		else:
			self.type = value
	def empty_slots(self):
		# return the empty slots of the pizza
		empty = []
		if self.type == None:
			empty.append('pizza_type')
		if self.crust == None:
			empty.append('crust')
		if self.size == None:
			empty.append('size')
		return empty

	def _populate_toppings(self):
		toppings_map = {'hawaiian': {'pineapple','ham','mozzarella'},
						'meat_lovers':{'mozzarella','pepperoni','ham','bacon','sausage'},
						'cheese':{'mozzarella','cheddar','swiss','provolone'},
						'pepperoni':{'mozzarella','pepperoni'},
						'veggie_supreme':{'mozzarella','green_peppers','red_onions','mushrooms','black_olives'},
						'vegan':{'green_peppers','red_onions','mushrooms','black_olives'}}
		if self.type:
			return toppings_map[self.type]
		else:
			return set()
	def _calculate_pie_price(self,DB):
		# compute price based on specialty, size, and crust
		if len(self.toppings) == 0 or not self.crust or not self.size:
			raise KeyError("The pizza is not complete!")
		else:
			# call the price db and calculatet
			# the base price is the price of the crus
			price = next(c for c in DB['crusts'] if c['size']==self.size and c['name']==self.crust)['price']
			# add on the price for all toppings
			for topping in toppings:
				price += next(c for c in DB['toppings'] if c['name']==topping)['price']
			return price
