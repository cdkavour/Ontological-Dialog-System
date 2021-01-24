from DialogFrameSimple import DialogFrameSimple
from DialogAct import DialogAct
from DialogActTypes import DialogActTypes
import math,random

class DB:
    def __init__(self,path):
        with open(path) as f:
            self.data = pd.DataFrame(json.load(f))

class FrameDMSimple:

    def __init__(self, NLU, NLG):
        self.NLU = NLU
        self.NLG = NLG
        # define frame below, for example:
        self.DialogFrame = DialogFrameSimple()
        self.DB = DB('db.txt')

    def execute(self, inputStr):
        # apply the NLU component
        currentSemanticFrame = self.NLU.parse(inputStr)

        # update the dialog frame with the new information
        self.trackState(currentSemanticFrame)

        # and decide what to do next
        newDialogAct = self.selectDialogAct()

        # then generate some meaningful response
        response = self.NLG.generate(newDialogAct) 
        return response

    def trackState(self, newSemanticFrame):
        # update self.DialogFrame based on the contents of newSemanticFrame
        slots = []
        for s in ['pizza_type','crust','size','name','number','modality','adresss',
                  'ground_pizza','ground_order']:
            try:
                slots.append(newSemanticFrame.Slots[s])
            except KeyError:
                slots.append(None)
        self.DialogFrame.update(slots,self.DB)

    def selectDialogAct(self):
        # decide on what dialog act to execute
        # by default, return a Hello dialog act

        # check and see how far we are
        
        # have we grounded the order
        
        # have we grounded the pizza
        
        # is the order ready to be grounded
        
        # is the pizza ready to be grounded
        
        # what can we fill in next?

        dialogAct = DialogAct()
        dialogAct.DialogActType = DialogActTypes.HELLO
        return dialogAct

    def submit_order(self):
        # update db, including adding a current order for the user and 
        # updating the order index
        # and saving the text files
        cost = self.DialogFrame.calculate_price()
        num_digits = 5-int(math.log10(DB['order_idx']))+1
        confirmation_number = '0'*num_digits+str(DB['order_idx'])
        self.DB['open_orders'].append({'name':self.DialogFrame.user,
                            'confirmation_number':confirmation_number,
                            'status':'processing'}),

        self.DB['order_idx']+=1
        with open('db.txt') as f:
            json.dump(self.DB)
        return confirmation_number

