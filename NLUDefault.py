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


        # UNIVERSALS - cancel, repeat, start over
        if (inputStr == "cancel"):
            self.SemanticFrame.Slots["request"] = "cancel"
        elif (inputStr == "repeat"):
            self.SemanticFrame.Slots["request"] = "repeat"
        elif (inputStr == "start over"):
            self.SemanticFrame.Slots["request"] = "start_over"        



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
            self.SemanticFrame.Slots["pizza_type"] = "meatlovers"
        elif ("4 cheese" in inputStr):
            self.SemanticFrame.Intent = DialogActTypes.INFORM
            self.SemanticFrame.Slots["pizza_type"] = "4cheese"
        elif ("pepperoni" in inputStr):
            self.SemanticFrame.Intent = DialogActTypes.INFORM
            self.SemanticFrame.Slots["pizza_type"] = "pepperoni"
        elif ("veggie supreme" in inputStr):
            self.SemanticFrame.Intent = DialogActTypes.INFORM
            self.SemanticFrame.Slots["pizza_type"] = "veggiesupreme"
        elif ("vegan" in inputStr):
            self.SemanticFrame.Intent = DialogActTypes.INFORM
            self.SemanticFrame.Slots["pizza_type"] = "vegan"

        # Size
        if ("10 inch" in inputStr or "small" in inputStr):
            self.SemanticFrame.Intent = DialogActTypes.INFORM
            self.SemanticFrame.Slots["size"] = "small"
        elif ("12 inch" in inputStr or "medium" in inputStr):
            self.SemanticFrame.Intent = DialogActTypes.INFORM
            self.SemanticFrame.Slots["size"] = "medium"
        elif ("14 inch" in inputStr or "large" in inputStr):
            self.SemanticFrame.Intent = DialogActTypes.INFORM
            self.SemanticFrame.Slots["size"] = "large"

        # Crust
        if ("thin" in inputStr):
            self.SemanticFrame.Intent = DialogActTypes.INFORM
            self.SemanticFrame.Slots["crust"] = "thin"
        elif ("regular" in inputStr):
            self.SemanticFrame.Intent = DialogActTypes.INFORM
            self.SemanticFrame.Slots["crust"] = "regular"
        elif ("deep dish" in inputStr):
            self.SemanticFrame.Intent = DialogActTypes.INFORM
            self.SemanticFrame.Slots["crust"] = "deepdish"
        elif ("gluten free" in inputStr):
            self.SemanticFrame.Intent = DialogActTypes.INFORM
            self.SemanticFrame.Slots["crust"] = "glutenfree"

        # Name
        if("alexa" in inputStr):
            self.SemanticFrame.Intent = DialogActTypes.INFORM
            self.SemanticFrame.Slots["name"] = "alexa"
        elif("alex" in inputStr):
            self.SemanticFrame.Intent = DialogActTypes.INFORM
            self.SemanticFrame.Slots["name"] = "alex"

        # Pickup or Delivery
        if ("pick-up" in inputStr):
            self.SemanticFrame.Intent = DialogActTypes.INFORM
            self.SemanticFrame.Slots["transportation"] = "pick-up"
        elif ("delivery" in inputStr):
            self.SemanticFrame.Intent = DialogActTypes.INFORM
            self.SemanticFrame.Slots["transportation"] = "delivery"

        # Phone Number
        phone_number_match = re.search(r"(\d\d\d-\d\d\d-\d\d\d\d)", inputStr)
        if (phone_number_match):
            self.SemanticFrame.Intent = DialogActTypes.INFORM
            self.SemanticFrame.Slots["phone-number"] = phone_number_match.groups()[0]

        # Unsure of Intent
        else:
            self.SemanticFrame.Intent = DialogActTypes.UNDEFINED

        return self.SemanticFrame
