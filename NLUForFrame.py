from SemanticFrame import SemanticFrame
from DialogActTypes import DialogActTypes
import re

class NLUForFrame:

    def __init__(self):
        self.SemanticFrame = SemanticFrame()

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

    def parse(self, inputStr):
        # NLU COMPONENT CAN OUTPUT THE FOLLOWING DIALOG ACTS:
        # HELLO, GOODBYE, CONFIRM, DENY, INFROM, and REQUEST
        # ^ Tracked by the Semantic Frame's Intent

        # NLU component can fill slots for pizza type, crust type,
        # and size.
        inputStr = inputStr.lower()

        # Assume DOMAIN is always Pizza.
        self.SemanticFrame.Domain = "pizza"
        self.SemanticFrame.Intent = DialogActTypes.UNDEFINED

        # 5) INFORM
        # preferred order
        if ('modify preferred order' in inputStr):
            self.SemanticFrame.Intent = DialogActTypes.INFORM
            self.SemanticFrame.Slots['revise_preferred'] = True
            self.SemanticFrame.Slots['need_to_clear'] = True
        elif ('preferred' in inputStr or 'previous order' in inputStr):
            self.SemanticFrame.Intent = DialogActTypes.INFORM
            self.SemanticFrame.Slots['preferred'] = True

        # for multiple pizza ordering
        if ('done ordering' in inputStr):
            self.SemanticFrame.Intent = DialogActTypes.INFORM
            self.SemanticFrame.Slots['done_ordering'] = True

        # Pizza Type
        pizza_types_match = re.search(self.pizza_types_re,inputStr)
        if pizza_types_match:
            self.SemanticFrame.Intent = DialogActTypes.INFORM
            self.SemanticFrame.Slots['pizza_type'] = pizza_types_match[0]

        # Toppings
        negated_toppings_match = re.findall(self.negated_toppings_re,inputStr)
        if len(negated_toppings_match) > 0:
            if self.SemanticFrame.Slots['no toppings']:
                self.SemanticFrame.Slots['no toppings'] = self.SemanticFrame.Slots['no toppings'].union(negated_toppings_match)
            else:
                self.SemanticFrame.Slots['no toppings'] = set(negated_toppings_match)
                self.SemanticFrame.Intent = DialogActTypes.INFORM
        toppings_match = re.findall(self.toppings_re,inputStr)
        if len(toppings_match) > 0:
            if self.SemanticFrame.Slots['toppings']:
                self.SemanticFrame.Slots['toppings'] = self.SemanticFrame.Slots['toppings'].union(toppings_match)
            else:
                self.SemanticFrame.Slots['toppings'] = set(toppings_match)
            self.SemanticFrame.Intent = DialogActTypes.INFORM

        # Size
        if ("10 inch" in inputStr or "small" in inputStr):
            self.SemanticFrame.Intent = DialogActTypes.INFORM
            self.SemanticFrame.Slots["size"] = "small"
        if ("12 inch" in inputStr or "medium" in inputStr):
            self.SemanticFrame.Intent = DialogActTypes.INFORM
            self.SemanticFrame.Slots["size"] = "medium"
        if ("14 inch" in inputStr or "large" in inputStr):
            self.SemanticFrame.Intent = DialogActTypes.INFORM
            self.SemanticFrame.Slots["size"] = "large"

        # Crust
        crusts_match = re.search(self.crusts_re,inputStr)  
        if crusts_match:
            self.SemanticFrame.Intent = DialogActTypes.INFORM
            self.SemanticFrame.Slots["crust"] = crusts_match[0]       

        # Name
        users_match = re.search(self.users_re,inputStr)
        if users_match:
            self.SemanticFrame.Intent = DialogActTypes.INFORM
            self.SemanticFrame.Slots["name"] = users_match[0]

        # Pickup or Delivery
        if ('update delivery method' in inputStr):
        	self.SemanticFrame.Intent = DialogActTypes.INFORM
        	self.SemanticFrame.Slots['update_modality'] = True
        elif ("pick-up" in inputStr):
            self.SemanticFrame.Intent = DialogActTypes.INFORM
            self.SemanticFrame.Slots["modality"] = "pick-up"
        elif ("delivery" in inputStr):
            self.SemanticFrame.Intent = DialogActTypes.INFORM
            self.SemanticFrame.Slots["modality"] = "delivery"
        
        # address 
        address_match = re.search(r"([0-9]+ [0-9A-z#\.\- ]{1,}[A-z]+[0-9A-z#\.\- ]+)",inputStr)
        if (address_match and not address_match[0]=='4 cheese'):
            self.SemanticFrame.Intent = DialogActTypes.INFORM
            self.SemanticFrame.Slots["address"] = address_match[0]
        
        # phone number
        phone_number_match = re.search(r"((\+{0,1}1[- ]){0,1}(\(*[0-9]{3}\)*){0,1}[- ( - )]{0,1}[0-9]{3}[- ( - )]{0,1}[0-9]{4})", inputStr)
        if (phone_number_match):
            self.SemanticFrame.Intent = DialogActTypes.INFORM
            self.SemanticFrame.Slots["number"] = phone_number_match[0]

        # HELLO
        if ("hello" in inputStr):
            self.SemanticFrame.Intent = DialogActTypes.HELLO
        # GOODBYE
        elif ("goodbye" in inputStr):
            self.SemanticFrame.Intent = DialogActTypes.GOODBYE
        # CONFIRM
        elif ("yes" in inputStr):
            self.SemanticFrame.Intent = DialogActTypes.CONFIRM
        # DENY
        elif ("no" in inputStr and len(negated_toppings_match)==0):
            self.SemanticFrame.Intent = DialogActTypes.DENY
        
        # REQUEST
        # UNIVERSALS - cancel, repeat, start over
        if (inputStr in ['cancel','repeat','start over'] ):
            self.SemanticFrame.Intent = DialogActTypes.REQUEST
            self.SemanticFrame.Slots["request"] = inputStr
        # order status
        elif ('status' in inputStr):
            self.SemanticFrame.Intent = DialogActTypes.REQUEST
            self.SemanticFrame.Slots['request'] = 'status'

        return self.SemanticFrame