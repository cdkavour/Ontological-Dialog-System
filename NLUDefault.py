from SemanticFrame import SemanticFrame
from DialogActTypes import DialogActTypes
import re

class NLUDefault:

    def __init__(self):
        self.SemanticFrame = SemanticFrame()

    def parse(self, inputStr):
        # NLU COMPONENT CAN OUTPUT THE FOLLOWING DIALOG ACTS:
        # HELLO, GOODBYE, CONFIRM, DENY, INFROM, and REQUEST
        # ^ Tracked by the Semantic Frame's Intent

        # NLU component can fill slots for pizza type, crust type,
        # and size.


        inputStr = inputStr.lower()

        # Assume DOMAIN is always Pizza.
        self.SemanticFrame.Domain = "pizza"
        
        phone_number_match = re.search(r"((\+{0,1}1[- ]){0,1}(\(*[0-9]{3}\)*){0,1}[- ( - )]{0,1}[0-9]{3}[- ( - )]{0,1}[0-9]{4})", inputStr)
        address_match = re.search(r"([0-9]+ [0-9A-z#\.\- ]{1,}[A-z]+[0-9A-z#\.\- ]+)",inputStr)
        
        # UNIVERSALS - cancel, repeat, start over
        if (inputStr in ['cancel','repeat','start over'] ):
            self.SemanticFrame.Intent = DialogActTypes.REQUEST
            self.SemanticFrame.Slots["request"] = inputStr   
        elif (inputStr == "preferred"):
            self.SemanticFrame.Intent = DialogActTypes.REQUEST
            self.SemanticFrame.Slots["request"] = "preferred"

        # 1) HELLO
        elif ("hello" in inputStr):
            self.SemanticFrame.Intent = DialogActTypes.HELLO

        # 2) GOODBYE
        elif ("goodbye" in inputStr):
            self.SemanticFrame.Intent = DialogActTypes.GOODBYE

        # 3) CONFIRM
        elif ("yes" in inputStr):
            self.SemanticFrame.Intent = DialogActTypes.CONFIRM

        # 4) DENY
        elif ("no" in inputStr):
            self.SemanticFrame.Intent = DialogActTypes.DENY

        # 5) INFORM
        # Pizza Type
        elif ("hawaiian" in inputStr):
            self.SemanticFrame.Intent = DialogActTypes.INFORM
            self.SemanticFrame.Slots["pizza_type"] = "Hawaiian"
        elif ("meat lovers" in inputStr):
            self.SemanticFrame.Intent = DialogActTypes.INFORM
            self.SemanticFrame.Slots["pizza_type"] = "meat lovers"
        elif ("4 cheese" in inputStr):
            self.SemanticFrame.Intent = DialogActTypes.INFORM
            self.SemanticFrame.Slots["pizza_type"] = "4 cheese"
        elif ("pepperoni" in inputStr):
            self.SemanticFrame.Intent = DialogActTypes.INFORM
            self.SemanticFrame.Slots["pizza_type"] = "pepperoni"
        elif ("veggie supreme" in inputStr):
            self.SemanticFrame.Intent = DialogActTypes.INFORM
            self.SemanticFrame.Slots["pizza_type"] = "veggie supreme"
        elif ("vegan" in inputStr):
            self.SemanticFrame.Intent = DialogActTypes.INFORM
            self.SemanticFrame.Slots["pizza_type"] = "vegan"

        # Size
        elif ("10 inch" in inputStr or "small" in inputStr):
            self.SemanticFrame.Intent = DialogActTypes.INFORM
            self.SemanticFrame.Slots["size"] = "small"
        elif ("12 inch" in inputStr or "medium" in inputStr):
            self.SemanticFrame.Intent = DialogActTypes.INFORM
            self.SemanticFrame.Slots["size"] = "medium"
        elif ("14 inch" in inputStr or "large" in inputStr):
            self.SemanticFrame.Intent = DialogActTypes.INFORM
            self.SemanticFrame.Slots["size"] = "large"

        # Crust
        elif ("thin" in inputStr):
            self.SemanticFrame.Intent = DialogActTypes.INFORM
            self.SemanticFrame.Slots["crust"] = "thin"
        elif ("regular" in inputStr):
            self.SemanticFrame.Intent = DialogActTypes.INFORM
            self.SemanticFrame.Slots["crust"] = "regular"
        elif ("deep dish" in inputStr):
            self.SemanticFrame.Intent = DialogActTypes.INFORM
            self.SemanticFrame.Slots["crust"] = "deep dish"
        elif ("gluten-free" in inputStr):
            self.SemanticFrame.Intent = DialogActTypes.INFORM
            self.SemanticFrame.Slots["crust"] = "gluten-free"

        # Name
        elif(inputStr in ['Peter','Paul','Mary']):
            self.SemanticFrame.Intent = DialogActTypes.INFORM
            self.SemanticFrame.Slots["name"] = inputStr

        # Pickup or Delivery
        elif ("pick-up" in inputStr):
            self.SemanticFrame.Intent = DialogActTypes.INFORM
            self.SemanticFrame.Slots["modality"] = "pick-up"
        elif ("delivery" in inputStr):
            self.SemanticFrame.Intent = DialogActTypes.INFORM
            self.SemanticFrame.Slots["modality"] = "delivery"
        elif (address_match):
            self.SemanticFrame.Intent = DialogActTypes.INFORM
            self.SemanticFrame.Slots["address"] = address_match.groups()[0]
        # phone number
        elif (phone_number_match):
            self.SemanticFrame.Intent = DialogActTypes.INFORM
            self.SemanticFrame.Slots["number"] = phone_number_match.groups()[0]
        
        # Unsure of Intent
        else:
            self.SemanticFrame.Intent = DialogActTypes.UNDEFINED

        return self.SemanticFrame
