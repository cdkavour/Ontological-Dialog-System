from DialogFrameSimple import DialogFrameSimple
from DialogAct import DialogAct
from DialogActTypes import DialogActTypes
import math,random,json
import pdb

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
        self.DB = DB('db.json').data
        self.NLG = NLG
        self.NLU.setDB(self.DB)
        self.lastDialogAct = None
        self.currentSemanticFrame = None

    def execute(self, inputStr):
        # apply the NLU component
        #import pdb;pdb.set_trace()
        self.currentSemanticFrame = self.NLU.parse(inputStr)

        #pdb.set_trace()

        # update the dialog frame with the new information
        self.trackState()
        change = False
        if self.PreviousSlots != self.currentSemanticFrame.Slots and len(self.PreviousSlots.keys()) == len(self.currentSemanticFrame.Slots.keys()):
                change = True
        
        # and decide what to do next
        newDialogAct = self.selectDialogAct()
        newDialogAct.change = change

        try:
            # update semantic frame based on user's request
            if self.currentSemanticFrame.Slots["request"] == "cancel":
                self.currentSemanticFrame.Slots = {}
            elif self.currentSemanticFrame.Slots["request"] == "start over":
                self.currentSemanticFrame.Slots = {}
            elif self.currentSemanticFrame.Slots["request"] == "repeat":
                self.currentSemanticFrame.Slots["request"] = None
            elif self.currentSemanticFrame.Slots["request"] == "status":
                if self.DialogFrame.user is not None:
                    self.currentSemanticFrame.Slots["request"] = None
        except KeyError:
            pass


        # then generate some meaningful response
        response = self.NLG.generate(newDialogAct)
        # if self.lastDialogAct.complete:
        #     self.submit_order()
        return response

    def trackState(self):

        # Confirm or deny pizza
        if self.currentSemanticFrame.Intent == DialogActTypes.CONFIRM and \
                                    type(self.lastDialogAct.slot)==tuple \
                                    and self.lastDialogAct.slot[0]==0:
            self.currentSemanticFrame.Slots['ground_pizza'] = True
        elif self.currentSemanticFrame.Intent == DialogActTypes.DENY and \
                                    type(self.lastDialogAct.slot)==tuple \
                                    and self.lastDialogAct.slot[0]==0:
            self.currentSemanticFrame.Slots['pizza_type'] = None
            self.currentSemanticFrame.Slots['crust'] = None
            self.currentSemanticFrame.Slots['size'] = None

        # Confirm or deny order
        if self.currentSemanticFrame.Intent == DialogActTypes.CONFIRM and \
                                    type(self.lastDialogAct.slot)==tuple \
                                    and self.lastDialogAct.slot[0]==1:
            self.currentSemanticFrame.Slots['ground_order'] = True
        elif self.currentSemanticFrame.Intent == DialogActTypes.DENY and \
                                    type(self.lastDialogAct.slot)==tuple \
                                    and self.lastDialogAct.slot[0]==1:
            self.currentSemanticFrame.Slots['name'] = None
            self.currentSemanticFrame.Slots['number'] = None
            self.currentSemanticFrame.Slots['modality'] = None
            self.currentSemanticFrame.Slots['address'] = None


        # update self.DialogFrame based on the contents of newSemanticFrame
        slots = []
        for s in ['pizza_type','crust','size','name','number','modality','address',
                  'ground_pizza','ground_order', 'request']:
            try:
                slots.append(self.currentSemanticFrame.Slots[s])
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

        #pdb.set_trace()

        # by default, return a Hello dialog act
        dialogAct.DialogActType = DialogActTypes.HELLO

        if len(self.currentSemanticFrame.Slots.keys())>0 and self.PreviousSlots == self.currentSemanticFrame.Slots:
            # we need to reqalts
            dialogAct.DialogActType = DialogActTypes.REQALTS
            dialogAct.slot = self.lastDialogAct.slot

        elif self.DialogFrame.request == "cancel":
            dialogAct.DialogActType = DialogActTypes.GOODBYE

        elif self.DialogFrame.request == "repeat":
            dialogAct.DialogActType = DialogActTypes.REQALTS
            dialogAct.slot = self.lastDialogAct.slot

        elif self.DialogFrame.request == "start over":
            dialogAct.DialogActType = DialogActTypes.HELLO

        elif self.DialogFrame.request == "status":
            dialogAct.DialogActTypes = DialogActTypes.INFORM
            dialogAct.slot = self.DialogFrame.order_status


        # Order has been grounded; return goodbye diolog act
        elif self.DialogFrame.ground_order == True:
            dialogAct.DialogActType = DialogActTypes.GOODBYE
            dialogAct.complete = True
        
        # Pizza grounded, order not grounded
        elif self.DialogFrame.ground_pizza == True:

            # Get user if needed
            if not self.DialogFrame.name:
                dialogAct.DialogActType = DialogActTypes.REQUEST
                dialogAct.slot = "name"

            # Get modality if needed
            elif not self.DialogFrame.modality:
                dialogAct.DialogActType = DialogActTypes.REQUEST
                dialogAct.slot = "modality"

            # Get address if needed
            elif self.DialogFrame.modality == "delivery" and not self.DialogFrame.address:
                dialogAct.DialogActType = DialogActTypes.REQUEST
                dialogAct.slot = "address"
        
            # Ground Order
            else:
                dialogAct.DialogActType = DialogActTypes.REQUEST
                dialogAct.slot = (1,self.currentSemanticFrame.Slots)
    
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
            else:
                dialogAct.DialogActType = DialogActTypes.REQUEST
                dialogAct.slot = (0,self.currentSemanticFrame.Slots)
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

