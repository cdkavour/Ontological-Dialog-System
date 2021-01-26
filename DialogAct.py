from DialogActTypes import DialogActTypes

class DialogAct:

    def __init__(self):
       	self.DialogActType = DialogActTypes.UNDEFINED
        self.slot = None
        self.change = None
        # add whatever else you want a dialog act to contain here
        # some suggestions: strings, elements of the dialog frame, etc.
	
