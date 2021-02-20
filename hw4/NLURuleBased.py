from SemanticFrame import SemanticFrame
from DialogActTypes import DialogActTypes
from Rules import Rules
import re
import pdb
from collections import defaultdict

class NLURuleBased:

    def __init__(self):
        self.SemanticFrame = SemanticFrame()
        self.Rules = Rules()

        # Intent matching Regex's
        self.make_pizza_matcher = re.compile(r"|".join(self.Rules.MAKE_PIZZA_RULES))
        self.add_modality_matcher = re.compile(r"|".join(self.Rules.ADD_MODALITY_RULES))
        self.greet_matcher = re.compile(r"|".join(self.Rules.GREET_RULES))
        self.add_personal_matcher = re.compile(r"|".join(self.Rules.ADD_PERSONAL_RULES))
        self.order_preferred_matcher = re.compile(r"|".join(self.Rules.ORDER_PREFERRED_RULES))
        self.check_order_status_matcher = re.compile(r"|".join(self.Rules.CHECK_ORDER_STATUS_RULES))
        self.thank_matcher = re.compile(r"|".join(self.Rules.THANK_RULES))
        self.update_modality_matcher = re.compile(r"|".join(self.Rules.UPDATE_MODALITY_RULES))
        self.add_attribute_matcher = re.compile(r"|".join(self.Rules.ADD_ATTRIBUTE_RULES))
        self.add_payment_attribute_matcher = re.compile(r"|".join(self.Rules.ADD_PAYMENT_ATTRIBUTE_RULES))
        self.confirm_matcher = re.compile(r"|".join(self.Rules.CONFIRM_RULES))
        self.deny_matcher = re.compile(r"|".join(self.Rules.DENY_RULES))
        self.depart_matcher = re.compile(r"|".join(self.Rules.DEPART_RULES))
        self.end_ordering_matcher = re.compile(r"|".join(self.Rules.END_ORDERING_RULES))
        self.modify_order_preferred_matcher = re.compile(r"|".join(self.Rules.MODIFY_PREFERRED_ORDER_RULES))
        self.modify_order_modality_matcher = re.compile(r"|".join(self.Rules.MODIFY_ORDER_MODALITY_RULES))
        self.remove_attribute_matcher = re.compile(r"|".join(self.Rules.REMOVE_ATTRIBUTE_RULES))
        self.request_matcher = re.compile(r"|".join(self.Rules.REQUEST_RULES))
        self.request_cost_of_matcher = re.compile(r"|".join(self.Rules.REQUEST_COST_OF_RULES))
        self.request_listing_matcher = re.compile(r"|".join(self.Rules.REQUEST_LISTING_RULES))
        self.start_ordering_matcher = re.compile(r"|".join(self.Rules.START_ORDERING_RULES))
        self.update_attribute_matcher = re.compile(r"|".join(self.Rules.UPDATE_ATTRIBUTE_RULES))
        self.update_modality_matcher = re.compile(r"|".join(self.Rules.UPDATE_MODALITY_RULES))
        self.update_payment_attribute_matcher = re.compile(r"|".join(self.Rules.UPDATE_PAYMENT_ATTRIBUTE_RULES))
        self.update_personal_matcher = re.compile(r"|".join(self.Rules.UPDATE_PERSONAL_RULES))
        self.add_to_order_matcher = re.compile(r"|".join(self.Rules.ADD_TO_ORDER_RULES))
        self.update_matcher = re.compile(r"|".join(self.Rules.UPDATE_RULES))
        self.inform_matcher = re.compile(r"|".join(self.Rules.INFORM_RULES))

        # Slot matching Regex's
        self.crust_matcher = re.compile(r"|".join(self.Rules.CRUSTS))
        self.size_matcher = re.compile(r"|".join(self.Rules.SIZES))
        self.pizza_type_matcher = re.compile(r"|".join(self.Rules.PIZZA_TYPES))
        self.modality_matcher = re.compile(r"|".join(self.Rules.MODALITIES))
        self.cost_matcher = re.compile(r"|".join(self.Rules.COSTS))
        self.name_matcher = re.compile(r"|".join(self.Rules.NAMES))
        self.number_matcher = re.compile(r"|".join(self.Rules.NUMBERS))
        self.numeric_matcher = re.compile(r"|".join(self.Rules.NUMERICS))
        self.quant_matcher = re.compile(r"|".join(self.Rules.QUANTS))
        self.address_matcher = re.compile(r"|".join(self.Rules.ADDRESSES))
        self.beverage_matcher = re.compile(r"|".join(self.Rules.BEVERAGES))
        self.payment_matcher = re.compile(r"|".join(self.Rules.PAYMENTS))
        self.side_matcher = re.compile(r"|".join(self.Rules.SIDES))
        self.store_matcher = re.compile(r"|".join(self.Rules.STORES))
        self.time_matcher = re.compile(r"|".join(self.Rules.TIMES))
        self.topping_matcher = re.compile(r"|".join(self.Rules.TOPPINGS))
        self.topping_type_matcher = re.compile(r"|".join(self.Rules.TOPPING_TYPES))

    # Slot annotation regex functions
    def tag_crusts(self, input):
        return re.sub(r"|".join(self.Rules.CRUSTS), r'<crust>\1\2\3\4</crust>', input)

    def tag_sizes(self, input):
        return re.sub(r"|".join(self.Rules.SIZES), r'<size>\1\2\3\4\5\6</size>', input)

    def tag_pizza_types(self, input):
        return re.sub(r"|".join(self.Rules.PIZZA_TYPES), r'<pizza_type>\1\2\3\4\5\6</pizza_type>', input)

    def tag_modalities(self, input):
        return re.sub(r"|".join(self.Rules.MODALITIES), r'<modality>\1\2\3\4\5</modality>', input)

    def tag_costs(self, input):
        return re.sub(r"|".join(self.Rules.COSTS), r'<cost>\1\2</cost>', input)

    def tag_names(self, input):
        return re.sub(r"|".join(self.Rules.NAMES), r'<name>\1\2\3</name>', input)

    def tag_numbers(self, input):
        return re.sub(r"|".join(self.Rules.NUMBERS), r'<number>\1</number>', input)

    def tag_numerics(self, input):
       return re.sub(r"|".join(self.Rules.NUMERICS), r'<numeric>\1</numeric>', input)

    def tag_quants(self, input):
        return re.sub(r"|".join(self.Rules.QUANTS), r'<quant>\1\2\3\4\5</quant>', input)

    def tag_addresses(self, input):
        return re.sub(r"|".join(self.Rules.ADDRESSES), r'<address>\1</address>', input)

    def tag_beverages(self, input):
        return re.sub(r"|".join(self.Rules.BEVERAGES), r'<beverage>\1\2\3\4\5\6</beverage>', input)

    def tag_payments(self, input):
        return re.sub(r"|".join(self.Rules.PAYMENTS), r'<payment>\1\2\3\4</payment>', input)

    def tag_sides(self, input):
        return re.sub(r"|".join(self.Rules.SIDES), r'<side>\1\2\3\4\5\6</side>', input)

    def tag_stores(self, input):
        return re.sub(r"|".join(self.Rules.STORES), r'<store>\1\2</store>', input)

    def tag_times(self, input):
        return re.sub(r"|".join(self.Rules.TIMES), r'<time>\1\2\3\4\5\6\7\8\9</time>', input)

    def tag_toppings(self, input):
        return re.sub(r"|".join(self.Rules.TOPPINGS), r'<topping>\1\2\3\4\5\6\7\8\9\10\11\12</topping>', input)

    def tag_topping_types(self, input):
        return re.sub(r"|".join(self.Rules.TOPPING_TYPES), r'<topping_type>\1\2\3\4\5\6</topping_type>', input)


    def clear_slots(self):
        self.SemanticFrame.Slots = defaultdict(lambda:None)

    def clearPizza(self):
        self.SemanticFrame.Slots['pizza_type'] = None
        self.SemanticFrame.Slots['size'] = None
        self.SemanticFrame.Slots['crust'] = None
        self.SemanticFrame.Slots['toppings'] = None
        self.SemanticFrame.Slots['no toppings'] = None
        self.SemanticFrame.Slots['ground_pizza'] = None

    def setDB(self,db):
        self.pizza_types_re = self._get_defaults_check(db)
        self.negated_toppings_re = self._get_negated_toppings_check(db)
        self.toppings_re = self._get_toppings_check(db)
        self.crusts_re, self.sizes_re = self._get_crusts_and_sizes_check(db)
        self.users_re = self._get_users_check(db)
    
    def _get_users_check(self,db):
        return re.compile(r'|'.join(set(db.users.name)).lower())
    def _get_defaults_check(self,db):
        return re.compile(r'|'.join(set(db.defaults.name)))
    def _get_toppings_check(self,db):
        return re.compile('(?<!no )({})'.format('|'.join(set(db.toppings.name))))
    def _get_negated_toppings_check(self,db):
        return re.compile('no ({})'.format('|'.join(set(db.toppings.name))))
    def _get_crusts_and_sizes_check(self,db):
        return re.compile(r'|'.join(set(db.crusts.name))),re.compile(r'|'.join(set(db.crusts['size'])))

    def printSemanticFrame(self):
        print(self.SemanticFrame)

    def parse(self, inputStr):
        # RULE BASED NLU COMPONENT CAN OUTPUT THE FOLLOWING DIALOG ACTS:

        inputStr = inputStr.lower()
        annotation = inputStr

        # Assume DOMAIN is always Pizza.
        self.SemanticFrame.Domain = "pizza"

        # MAKE PIZZA
        if(self.make_pizza_matcher.search(inputStr)):
            self.SemanticFrame.Intent = DialogActTypes.MAKE_PIZZA

        # ORDER_PREFERRED
        elif(self.order_preferred_matcher.search(inputStr)):
            self.SemanticFrame.Intent = DialogActTypes.ORDER_PREFERRED

        # MODIFY ORDER PREFERRED
        elif(self.modify_order_preferred_matcher.search(inputStr)):
            self.SemanticFrame.Intent = DialogActTypes.MODIFY_PREFERRED_ORDER

        # START ORDERING
        elif(self.start_ordering_matcher.search(inputStr)):
            self.SemanticFrame.Intent = DialogActTypes.START_ORDERING

        # CHECK_ORDER_STATUS
        elif(self.check_order_status_matcher.search(inputStr)):
            self.SemanticFrame.Intent = DialogActTypes.CHECK_ORDER_STATUS

        # END ORDERING
        elif(self.end_ordering_matcher.search(inputStr)):
            self.SemanticFrame.Intent = DialogActTypes.END_ORDERING




        # REQUEST COST OF
        elif(self.request_cost_of_matcher.search(inputStr)):
            self.SemanticFrame.Intent = DialogActTypes.REQUEST_COST_OF  

        # REQUEST LISTING
        elif(self.request_listing_matcher.search(inputStr)):
            self.SemanticFrame.Intent = DialogActTypes.REQUEST_LISTING




        # MODIFY ORDER MODALITY
        elif(self.modify_order_modality_matcher.search(inputStr)):
            self.SemanticFrame.Intent = DialogActTypes.MODIFY_ORDER_MODALITY

        # UPDATE_MODALITY
        elif(self.update_modality_matcher.search(inputStr)):
            self.SemanticFrame.Intent = DialogActTypes.UPDATE_MODALITY

        # ADD_MODALITY
        elif(self.add_modality_matcher.search(inputStr)):
            self.SemanticFrame.Intent = DialogActTypes.ADD_MODALITY

        # UPDATE PAYMENT ATTRIBUTE
        elif(self.update_payment_attribute_matcher.search(inputStr)):
            self.SemanticFrame.Intent = DialogActTypes.UPDATE_PAYMENT_ATTRIBUTE

        # ADD PAYMENT ATTRIBUTE
        elif(self.add_payment_attribute_matcher.search(inputStr)):
            self.SemanticFrame.Intent = DialogActTypes.ADD_PAYMENT_ATTRIBUTE

        # UPDATE PERSONAL
        elif(self.update_personal_matcher.search(inputStr)):
            self.SemanticFrame.Intent = DialogActTypes.UPDATE_PERSONAL

        # ADD_PERSONAL
        elif(self.add_personal_matcher.search(inputStr)):
            self.SemanticFrame.Intent = DialogActTypes.ADD_PERSONAL



        # UPDATE
        elif(self.update_matcher.search(inputStr)):
            self.SemanticFrame.Intent = DialogActTypes.UPDATE

        # INFORM
        elif(self.inform_matcher.search(inputStr)):
            self.SemanticFrame.Intent = DialogActTypes.INFORM

        # REQUEST
        elif(self.request_matcher.search(inputStr)):
            self.SemanticFrame.Intent = DialogActTypes.REQUEST



        # ADD TO ORDER
        elif(self.add_to_order_matcher.search(inputStr)):
            self.SemanticFrame.Intent = DialogActTypes.ADD_TO_ORDER


        # UPDATE ATTRIBUTE
        elif(self.update_attribute_matcher.search(inputStr)):
            self.SemanticFrame.Intent = DialogActTypes.UPDATE_ATTRIBUTE  

        # ADD_ATTRIBUTE
        elif(self.add_attribute_matcher.search(inputStr)):
            self.SemanticFrame.Intent = DialogActTypes.ADD_ATTRIBUTE

        # REMOVE ATTRIBUTE
        elif(self.remove_attribute_matcher.search(inputStr)):
            self.SemanticFrame.Intent = DialogActTypes.REMOVE_ATTRIBUTE

        # GREET
        elif(self.greet_matcher.search(inputStr)):
            self.SemanticFrame.Intent = DialogActTypes.GREET

        # THANK
        elif(self.thank_matcher.search(inputStr)):
            self.SemanticFrame.Intent = DialogActTypes.THANK

        # CONFIRM
        elif(self.confirm_matcher.search(inputStr)):
            self.SemanticFrame.Intent = DialogActTypes.CONFIRM

        # DENY
        elif(self.deny_matcher.search(inputStr)):
            self.SemanticFrame.Intent = DialogActTypes.DENY

        # DEPART
        elif(self.depart_matcher.search(inputStr)):
            self.SemanticFrame.Intent = DialogActTypes.DEPART

        # Unsure of Intent
        else:
            self.SemanticFrame.Intent = DialogActTypes.UNDEFINED

        # Tag Slots
        crusts = self.crust_matcher.search(inputStr)
        if crusts:
            self.SemanticFrame.Slots['crust'] = crusts[0]
            annotation = self.tag_crusts(annotation)

        sizes = self.size_matcher.search(inputStr)
        if sizes:
            self.SemanticFrame.Slots['size'] = sizes[0]
            annotation = self.tag_sizes(annotation)

        pizza_types = self.pizza_type_matcher.search(inputStr)
        if pizza_types:
            self.SemanticFrame.Slots['pizza_type'] = pizza_types[0]
            annotation = self.tag_pizza_types(annotation)

        modalities = self.modality_matcher.search(inputStr)
        if modalities:
            self.SemanticFrame.Slots['modality'] = modalities[0]
            annotation = self.tag_modalities(annotation)

        costs = self.cost_matcher.search(inputStr)
        if costs:
            self.SemanticFrame.Slots['cost'] = costs[0]
            annotation = self.tag_costs(annotation)

        names = self.name_matcher.search(inputStr)
        if names:
            self.SemanticFrame.Slots['name'] = names[0]
            annotation = self.tag_names(annotation)

        # Only get numeric if no phone number
        numbers = self.number_matcher.search(inputStr)
        if numbers:
            self.SemanticFrame.Slots['number'] = numbers[0]
            annotation = self.tag_numbers(annotation)
        else:
            numeric = self.numeric_matcher.search(inputStr)
            if numeric:
                self.SemanticFrame.Slots['numeric'] = numeric[0]
                annotation = self.tag_numerics(annotation)

        quants = self.quant_matcher.search(inputStr)
        if quants:
            self.SemanticFrame.Slots['quant'] = quants[0]
            annotation = self.tag_quants(annotation)

        addresses = self.address_matcher.search(inputStr)
        if addresses:
            self.SemanticFrame.Slots['address'] = addresses[0]
            annotation = self.tag_addresses(annotation)

        beverages = self.beverage_matcher.search(inputStr)
        if beverages:
            self.SemanticFrame.Slots['beverage'] = beverages[0]
            annotation = self.tag_beverages(annotation)      

        payments = self.payment_matcher.search(inputStr)
        if payments:
            self.SemanticFrame.Slots['payment'] = payments[0]
            annotation = self.tag_payments(annotation)

        sides = self.side_matcher.search(inputStr)
        if sides:
            self.SemanticFrame.Slots['side'] = sides[0]
            annotation = self.tag_sides(annotation)

        stores = self.store_matcher.search(inputStr)
        if stores:
            self.SemanticFrame.Slots['store'] = stores[0]
            annotation = self.tag_stores(annotation)

        times = self.time_matcher.search(inputStr)
        if times:
            self.SemanticFrame.Slots['time'] = times[0]
            annotation = self.tag_times(annotation)

        toppings = self.topping_matcher.search(inputStr)
        if toppings:
            self.SemanticFrame.Slots['topping'] = toppings[0]
            annotation = self.tag_toppings(annotation)

        topping_types = self.topping_type_matcher.search(inputStr)
        if topping_types:
            self.SemanticFrame.Slots['topping_types'] = topping_types[0]
            annotation = self.tag_topping_types(annotation) 

        return annotation