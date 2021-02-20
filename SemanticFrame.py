from collections import defaultdict

class SemanticFrame:

    def __init__(self):
        self.Domain = None
        self.Intent = None
        self.Slots = defaultdict(lambda:None)

    def __str__(self):
        retstr = "Intent: {}\n".format(self.Intent)
        retstr += "Slots:\n"
        for (slotname, slotval) in self.Slots.items():
            retstr += "{} {}\n".format(slotname, slotval)

        return retstr
