from DialogFrameSimple import DialogFrameSimple
from DialogAct import DialogAct
from DialogActTypes import DialogActTypes
import math,random,json

class DB:
    def __init__(self,path):
        with open(path) as f:
            self.data = json.load(f)

class FrameDMSimple:

    def __init__(self, NLU, NLG):
        self.NLU = NLU
        # define frame below, for example:
        self.PreviousSlots = {}
        self.DialogFrame = DialogFrameSimple()
        self.DB = DB('db.json')
        self.NLG = NLG
        self.NLU.setDB(self.DB)
        self.lastDialogAct = None

    def execute(self, inputStr):
        # apply the NLU component
        import pdb;pdb.set_trace()
        currentSemanticFrame = self.NLU.parse(inputStr)
        self.currentSemanticFrame = currentSemanticFrame
        # update the dialog frame with the new information
        self.trackState(currentSemanticFrame)
        change = False
        if self.PreviousSlots != currentSemanticFrame.Slots and len(self.PreviousSlots.keys()) == len(currentSemanticFrame.Slots.keys()):
                change = True
        
        # and decide what to do next
        newDialogAct = self.selectDialogAct()
        newDialogAct.change = change

        # then generate some meaningful response
        response = self.NLG.generate(newDialogAct)
        if self.lastDialogAct.complete:
            self.submit_order()
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
        # idx of 0=denied pizza,1=dineid the order, 2= else
        # if 0:
        #     delete pizza slots
        # if 1: 
        #     delete person modality and address


        self.DialogFrame.update(slots,self.DB)

    def selectDialogAct(self):
        dialogAct = DialogAct()

        # by default, return a Hello dialog act
        dialogAct.DialogActType = DialogActTypes.HELLO

        if len(self.currentSemanticFrame.Slots.keys())>0 and self.PreviousSlots == self.currentSemanticFrame.Slots:
            # we need to reqalts
            dialogAct.DialogActType = DialogActTypes.REQALTS
            dialogAct.slot = self.lastDialogAct.slot

        # Order has been grounded; return goodbye diolog act
        elif self.DialogFrame.ground_order == True:
            dialogAct.DialogActType = DialogActTypes.GOODBYE
            dialogAct.complete = True
        
        # Pizza grounded, order not grounded
        elif self.DialogFrame.ground_pizza == True:

            # Get user if needed
            if not self.DialogFrame.user:
                dialogAct.DialogActType = DialogActTypes.REQUEST
                dialogAct.slot = "name"

            # Get modality if needed
            elif not self.DialogFrame.modality:
                dialogAct.DialogActType = DialogActTypes.REQUEST
                dialogAct.slot = "modality"

            # Get address if needed
            elif DialogFrame.modality == "delivery" and not self.DialogFrame.address:
                dialogAct.DialogActType = DialogActTypes.REQUEST
                dialogAct.slot = "address"
        
            # Ground Order
            else:
                dialogAct.DialogActType = DialogActTypes.REQUEST
                dialogAct.slot = (1,self.DialogFrame)
    
        # Pizza not yet grounded
        else:

            # Get pizza type if needed
            if not self.DialogFrame.pizza.type:
                dialogAct.DialogActType = DialogActTypes.REQUEST
                dialogAct.slot = "pizza_type"
            # Get crust if needed
            elif not self.DialogFrame.pizza.crust:
                dialogAct.DialogActType = DialogActTypes.REQUEST
                dialogAct.slot = "crust"

            # Get size if needed
            elif not self.DialogFrame.pizza.size:
                dialogAct.DialogActType = DialogActTypes.REQUEST
                dialogAct.slot = "size"

            # Ground Pizza
            elif not self.DialogFrame.pizza.size:
                dialogAct.DialogActType = DialogActTypes.REQUEST
                dialogAct.slot = (0,self.DialogFrame)
        # TODO 
        self.lastDialogAct = dialogAct
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

