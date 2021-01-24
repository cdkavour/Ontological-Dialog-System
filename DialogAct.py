from DialogActTypes import DialogActTypes

class DialogAct:
    def __init__(self,da_type=None,slot=None):
        if da_type:
        	self.DialogActType = DialogActTypes(da_type)
        else:
        	self.DialogActType = DialogActTypes.UNDEFINED
        self.slot = slot
        
        # add whatever else you want a dialog act to contain here
        # some suggestions: strings, elements of the dialog frame, etc.
	