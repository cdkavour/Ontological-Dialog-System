class Rules:

  def __init__(self):

    # INTENT REGEX MATCHES
    self.MAKE_PIZZA_RULES = [
      "i'll have",
      "i want to order",
      "i'd like to order",
      "may i order",
      "i'll order",
      "can i order",
      #"i need",
      #"let's go with",
      #"can i get",
      #"could i get",
    ]

    self.ADD_PAYMENT_ATTRIBUTE_RULES = [
      "card",
      "code",
      "expiration",
      "number",
      # "date",
      "security",
    ]

    self.ADD_TO_ORDER_RULES = [
      "cola",
      "soda",
      "root beer",
      "ceasar",
      "salad",
      "side",
    ]

    self.ADD_MODALITY_RULES = [
      "delivery",
      "take out",
      "take-out",
      "pick up",
      "pick-up",
    ]

    self.GREET_RULES = [
      "hello",
      "how's it going",
      "hi",
      "hi!",
      "hey",
      "how's it going",
      "ring",
    ]

    self.ADD_PERSONAL_RULES = [
      r"((\+{0,1}1[- ]){0,1}(\(*[0-9]{3}\)*){0,1}[- ( - )]{0,1}[0-9]{3}[- ( - )]{0,1}[0-9]{4})",
      r"([0-9]+ [0-9A-z#\.\- ]{1,}[A-z]+[0-9A-z#\.\- ]+)",
      "eva",
      "michael",
      "paul",
      "peter",
      "mary",
    ]

    self.ORDER_PREFERRED_RULES = [
      "my usual",
      "reorder my preferred",
      "my favorite",
      "my most frequent",
      "my usual",
      "my preferred",
      "my most common",
      "my previous",
      "my most recent",
    ]

    self.CHECK_ORDER_STATUS_RULES = [
      "where's the pizza i ordered",
      "is my order ready",
      # "how long",
      # "when",
      # "where's",
      # "ready",
      # "order",
    ]

    self.THANK_RULES = [
      "thanks",
      "thank you"
    ]

    self.UPDATE_MODALITY_RULES = [
      "please switch my order",
    ]

    self.ADD_ATTRIBUTE_RULES = [
      "mozzarella",
      "cheddar",
      "swiss",
      "provolone",
      "pineappl",
      "green peppers",
      "red onions",
      "mushrooms",
      "black olives",
      #"pepperoni",
      "ham",
      "bacon",
      "sausage",
    ]

    self.CONFIRM_RULES = [
      "yes",
      "yeah",
      "yep",
      "absolutely",
      #"right",
      "great",
      #"okay",
      #"mhm",
      "amazing",
      "perfect",
    ]

    self.DENY_RULES = [
      "no",
      "nope",
    ]

    self.DEPART_RULES = [
      "bye",
      "you too",
      "bye-bye",
      "peace",
    ]

    self.END_ORDERING_RULES = [
      "that will be all",
      "that'll be all",
      "should be it",
      "that's it",
    ]

    self.MODIFY_ORDER_MODALITY_RULES = [
      "updmake that to delivery",
      "updmake that to pick up",
      "updmake that to pick-up",
      "updmake that to take out",
      "updmake that to take-out",

      "change my order to delivery",
      "change my order to pick up",
      "change my order to pick-up",
      "change my order to take out",
      "change my order to take-out",
    ]

    self.MODIFY_PREFERRED_ORDER_RULES = [
      "update my preferred",
      "change my preferred",
    ]

    self.REMOVE_ATTRIBUTE_RULES = [
      #"no <topping>",
      "without",
      "take off",
    ]

    self.REQUEST_RULES = [
      "do you have",
      "recommend",
    ]

    self.REQUEST_COST_OF_RULES = [
      "how much",
      "cost",
      "price",
      "prices",
      "money",
    ]

    self.REQUEST_LISTING_RULES = [
      "to drink",
      "what's in",
      "what is",
      "what kind",
      "what kinds",
      "do you have",
    ]

    self.START_ORDERING_RULES = [
      "place an order",
      "could i order",
      "like to order",
      "order a pizza",
    ]

    self.UPDATE_ATTRIBUTE_RULES = [
      "rather have",
      "rather get",
      "actually",
      "different",
      "no, i want",
      "i prefer",
      "on second thought",
    ]

    self.UPDATE_MODALITY_RULES = [
      #"actually",
      "make that delivery",
      "make that take out",
      "make that take-out",
      "make that pick up",
      "make that pick-up",
      "change it to delivery",
      "change it to takeout",
      "change it to take-out",
      "change it to pick up",
      "change it to pick-up",
    ]

    self.UPDATE_PAYMENT_ATTRIBUTE_RULES = [
      "[change|update].*card",
      "[change|update].*code",
      "[change|update].*expiration",
      "[change|update].*number",
      "[change|update].*security",
    ]

    self.UPDATE_PERSONAL_RULES = [
      r"wait ((\+{0,1}1[- ]){0,1}(\(*[0-9]{3}\)*){0,1}[- ( - )]{0,1}[0-9]{3}[- ( - )]{0,1}[0-9]{4})",
      r"wait ([0-9]+ [0-9A-z#\.\- ]{1,}[A-z]+[0-9A-z#\.\- ]+)",
      "wait eva",
      "wait michael",
      "wait paul",
      "wait peter",
      "wait mary",
    ]

    self.UPDATE_RULES = [
      "actually, change",
      "wait, change",
    ]

    self.INFORM_RULES = [
      "I would like",
      "I will get",
    ]

    


    # Slot regex matches

    # Slot regex matches

    # crust
    self.CRUSTS = [
      "(\S*thin\S*)",
      "(\S*regular\S*)",
      "(\S*deep dish\S*)",
      "(\S*gluten free\S*)",
    ]

    # size
    self.SIZES = [
      "(\S*small\S*)",
      "(\S*medium\S*)",
      "(\S*large\S*)",
      "(\S*10\"\S*)",
      "(\S*12\"\S*)",
      "(\S*14\"\S*)",
    ]

    # pizza type
    self.PIZZA_TYPES = [
      "(\S*hawaiian\S*)",
      "(\S*meat lovers\S*)",
      "(\S*4 cheese\S*)",
      "(\S*pepperoni\S*)",
      "(\S*veggie supreme\S*)",
      "(\S*vegan\S*)",
    ]

    # modality
    self.MODALITIES = [
      "(\S*delivery\S*)",
      "(\S*pick up\S*)",
      "(\S*pick-up\S*)",
      "(\S*take out\S*)",
      "(\S*take-out)"
    ]

    # cost
    self.COSTS = [
      "(\S*$[0-9]+\.[0-9]+\S*)",
      "(\S*$[0-9]+)"
    ]

    # name
    self.NAMES = [
      "(\S*peter\S*)",
      "(\S*paul\S*)",
      "(\S*mary\S*)",
      "(\S*michael),"
      "(\S*eva\S*)",
    ]

    # number
    self.NUMBERS = [
      r"((\+{0,1}1[- ]){0,1}(\(*[0-9]{3}\)*){0,1}[- ( - )]{0,1}[0-9]{3}[- ( - )]{0,1}[0-9]{4}\S*)",
    ]

    # TODO - improve, will over match already tagged slots
    # numeric
    self.NUMERICS = [
      r"([0-9]{2}[0-9]+)",
    ]

    # quant
    self.QUANTS = [
      "(\S*four\S*)",
      "(\S*three\S*)",
      "(\S*two\S*)",
      "(\S*one\S*)",
      "(\S*no\S*)",
    ]

    # address
    self.ADDRESSES = [
      "([0-9]{3,4} [Street|Ave])"
    ]

    # beverage
    self.BEVERAGES = [
      "(\S*cola\S*)",
      "(\S*root beer\S*)",
      "(\S*orange soda\S*)",
      "(\S*lemon soda\S*)",
      "(\S*mineral water\S*)",
      "(\S*ginger ale\S*)",
    ]
    
    # payment
    self.PAYMENTS = [
      "(\S*visa\S*)",
      "(\S*cash\S*)",
      " (\S*card)\S*",
      "(\S*mastercard)"
    ]

    # sides
    self.SIDES = [
      "(\S*bread stick\S*)",
      "(\S*breadstick\S*)",
      "(\S*cheese stick\S*)",
      "(\S*cheesestick\S*)",
      "(\S*green salad\S*)",
      "(\S*ceasar salad)"
    ]

    # store
    self.STORES = [
      "(\S*laurelhurst\S*)",
      "(\S*ballard\S*)",
    ]

    # time
    self.TIMES = [
      "(\S*[0-9|10|11|12] o'clock\S*)",
      "(\S*Monday\S*)",
      "(\S*Tuesday\S*)",
      "(\S*Wednesday\S*)",
      "(\S*Thursday\S*)",
      "(\S*Friday\S*)",
      "(\S*Saturday\S*)",
      "(\S*Sunday\S*)",
      "(\S*when it arrives\S*)",
    ]

    # topping
    self.TOPPINGS = [
      "(\S*mozzarella\S*)",
      "(\S*cheddar\S*)",
      "(\S*swiss\S*)",
      "(\S*provolone\S*)",
      "(\S*pineapple\S*)",
      "(\S*green peppers\S*)",
      "(\S*red onions\S*)",
      "(\S*mushrooms\S*)",
      "(\S*black olives\S*)",
      #"(pepperoni\S*)",
      " (\S*ham\S*)",
      "(\S*bacon\S*)",
      "(\S*sausage\S*)",
    ]

    # topping type
    self.TOPPING_TYPES = [
      " (\S*milk\S*)",
      "(\S*milkless\S*)",
      "(\S*dairy-free\S*)",
      "(\S*vegetables\S*)",
      "(\S*meaty\S*)",
      "(\S*dairy\S*)",
    ]