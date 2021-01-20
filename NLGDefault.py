from DialogAct import DialogAct
from DialogActTypes import DialogActTypes

class NLGDefault:

    def __init__(self):
        # add whatever fields you want here
        self.Name = "NLGDefault"

    def generate(self, dialogAct):
        if (dialogAct.DialogActType == DialogActTypes.HELLO):
            return "Hello, how's it going?"
        else:
            return "Not implemented yet"
