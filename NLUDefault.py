from SemanticFrame import SemanticFrame

class NLUDefault:

    def __init__(self):
        self.SemanticFrame = SemanticFrame()

    def parse(self, inputStr):
        self.SemanticFrame.Domain = "pizza"
        if (inputStr == "Hello"):
            self.SemanticFrame.Intent = "HELLO"
        elif (inputStr == "Order me a Hawaiian"):
            self.SemanticFrame.Intent = "INFORM"
            self.SemanticFrame.Slots["pizza_type"] = "Hawaiian"
        elif (inputStr == "yes"):
            self.SemanticFrame.Intent = "CONFIRM"

        return self.SemanticFrame
