from DialogAct import DialogAct
from DialogActTypes import DialogActTypes
import random

class NLGForFrame:
    def __init__(self):
        # add whatever fields you want here
        self.Name = "NLGDefault"
        self.hellos = ['Hello','Hello how I can help you?']

    def generate(self, dialogAct):
        outstr = ''
        if (dialogAct.DialogActType == DialogActTypes.HELLO):
            outstr += random.choice(self.hellos)
        elif dialogAct.updated:
            outstr += "Okay I've updated that.  "
        # GOODBYE
        # TODO make sure that the goodbye portion of the frame 
        # knows to add this
        elif (dialogAct.DialogActType == DialogActTypes.GOODBYE):
            if dialogAct.complete:
                 "Thanks, I got your order. Goodbye."
            else:
                outstr += "Ending session.  Thank you, goodbye."
        
        # CONFIRM
        elif (dialogAct.DialogActType == DialogActTypes.CONFIRM):
            outstr += "Yes."
        
        # DENY
        elif (dialogAct.DialogActType == DialogActTypes.DENY):
            outstr += "No."
        
        # INFORM
        elif (dialogAct.DialogActType == DialogActTypes.INFORM):
            if (dialogAct.slot == "crust"):
                outstr += "We have thin, regular, deep dish, and gluten-free crusts."
            elif (dialogAct.slot == "size"):
                outstr += "We have small, medium, and large sizes."
            elif (dialogAct.slot == "pizza"):
                outstr += "Our specialty pizzas are Hawaiian, meat lovers, 4 cheese, pepperoni, veggie surpreme, and vegan."
            else:
                outstr += "Not implemented yet"

        # REQUEST
        elif (dialogAct.DialogActType == DialogActTypes.REQUEST):
            if(dialogAct.slot == "pizza_type"):
                outstr += "Welcome to the pizza ordering system. What kind of pizza would you like?"
            elif(dialogAct.slot == "crust"):
                outstr += "What crust type? We have thin, regular, deep dish, gluten free."
            elif(dialogAct.slot == "size"):
                outstr += "What size?"
            elif(type(dialogAct.slot) == tuple and dialogAct.slot[0]==0): # TODO, this is now a list
                slots = dialogAct.slot[1]
                outstr += "I have a {} {} crust {} pizza, is that right?".format(slots['size'],slots['crust'],slots['pizza_type'])
            elif(dialogAct.slot == "name"):
                outstr += "Name?"
            elif(dialogAct.slot == "number"):
                outstr += "Phone Number?"
            elif(dialogAct.slot == "modality"):
                outstr += "Pick up or delivery?"
            elif(dialogAct.slot == "address"):
                outstr += "Address?"
            elif(type(dialogAct.slot)==tuple): # TODO this is now a list
                slots = dialogAct.slot[1]
                if slots['modality'] == 'pick-up':
                    outstr += "So that is a {} {} crust {} pizza, for {} for pick-up, is that right?".format(slots['size'],slots['crust'],slots['pizza_type'],slots['name'])
                else:
                    outstr += "So that is a {} {} crust {} pizza, for {} for delivery to {}, is that right?".format(slots['size'],slots['crust'],slots['pizza_type'],slots['name'],slots['address'])
            else:
                outstr += "Not implemented yet"

        # REQALTS
        elif (dialogAct.DialogActType == DialogActTypes.REQALTS):
            if(dialogAct.slot == "pizza_type"):
                outstr += "Sorry, I didn't get that. What pizza would you like?"
            elif(dialogAct.slot == "crust"):
                outstr += "Sorry, I didn't get that. What crust type? We have thin, regular, deep dish, gluten free."
            elif(dialogAct.slot == "size"):
                outstr += "Sorry, I didn't get that. What size?"
            elif(type(dialogAct.slot) == tuple and dialogAct.slot[0]==0): # TODO
                slots = dialogAct.slot[1]
                outstr += "Sorry, I didn't get that. I have a {} {} crust {} pizza, is that right?".format(slots['size'],slots['crust'],slots['pizza_type'])
            elif(dialogAct.slot == "name"):
                outstr += "Sorry, I didn't get that. Name?"
            elif(dialogAct.slot == "number"):
                outstr += "Sorry, I didn't get that. Phone Number?"
            elif(dialogAct.slot == "modality"):
                outstr += "Sorry, I didn't get that. Pick up or delivery?"
            elif(dialogAct.slot == "address"):
                outstr += "Sorry, I didn't get that. Address?"
            elif(type(dialogAct.slot)==tuple): #TODO
                slots = dialogAct.slot[1]
                if slots['modality']=='pick-up':
                    outstr += "Sorry, I need you to confirm, you want a {} {} crust {} pizza, for {} for pick-up, is that right?".format(slots['size'],slots['crust'],slots['pizza_type'],slots['name'])
                else:
                    outstr += "Sorry, I need you to confirm, you want a {} {} crust {} pizza, for {} for delivery to {}, is that right?".format(slots['size'],slots['crust'],slots['pizza_type'],slots['name'],slots['address'])
            else:
                outstr += "Not implemented yet"
        else:
            outstr += "Not implemented yet"
        return outstrs