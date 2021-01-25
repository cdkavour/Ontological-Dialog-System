from DialogActTypes import DialogActTypes

class DialogAct:
    def __init__(self,da_type,slot):
       	self.DialogActType = da_type
        self.slot = slot
        
        # add whatever else you want a dialog act to contain here
        # some suggestions: strings, elements of the dialog frame, etc.
	