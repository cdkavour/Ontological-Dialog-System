from DialogAct import DialogAct
from DialogActTypes import DialogActTypes

class NLGDefault:

    def __init__(self):
        # add whatever fields you want here
        self.Name = "NLGDefault"

    def generate(self, dialogAct):
    	# HELLO
        if (dialogAct.DialogActType == DialogActTypes.HELLO):
            return "Hello."

        # GOODBYE
        elif (dialogAct.DialogActType == DialogActTypes.GOODBYE):
        	return "Thanks, I got your order. Goodbye."

        # CONFIRM
        elif (dialogAct.DialogActType == DialogActTypes.CONFIRM):
        	return "Yes."

        # DENY
        elif (dialogAct.DialogActType == DialogActTypes.DENY):
        	return "No."


        # INFORM
        elif (dialogAct.DialogActType == DialogActTypes.INFORM):

        	if (dialogAct.slot == "crust"):
        		return "We have thin, regular, deepdish, and gloten free crusts."
        	elif (dialogAct.slot == "size"):
        		return "We have small, medium, and large sizes."
        	elif (dialogAct.slot == "pizza"):
        		return "Our specialty pizzas are hawaiian, meat lovers, 4 cheese, pepperoni, veggie surpreme, and vegan."
        	else:
        		return "Not implemented yet"


        # REQUEST
        elif (dialogAct.DialogActType == DialogActTypes.REQUEST):
        	if(dialogAct.slot == "pizza_type"):
        		return "Welcome to the pizza ordering system. What would you like?"
        	elif(dialogAct.slot == "crust"):
        		return "What crust type? We have thin, regular, deep dish, gluten free."
        	elif(dialogAct.slot == "size"):
        		return "What size?"
        	elif(type(dialogAct.slot) == tuple and dialogAct.slot[0]==0): # TODO, this is now a list
        		return "...ground pizza..."
        	elif(dialogAct.slot == "name"):
        		return "Name?"
        	elif(dialogAct.slot == "number"):
        		return "Phone Number?"
        	elif(dialogAct.slot == "modality"):
        		return "Pick up or delivery?"
        	elif(dialogAct.slot == "address"):
        		return "Address?"
        	elif(dialogAct.slot == "order"): # TODO this is now a list
        		return "...ground order..."

        	else:
        		return "Not implemented yet"

        # REQALTS
        elif (dialogAct.DialogActType == DialogActTypes.REQALTS):
        	if(dialogAct.slot == "pizza_type"):
        		return "Sorry, I didn't get that. What pizza would you like?"
        	elif(dialogAct.slot == "crust"):
        		return "Sorry, I didn't get that. Sorry, I didn't get that. What crust type? We have thin, regular, deep dish, gluten free."
        	elif(dialogAct.slot == "size"):
        		return "Sorry, I didn't get that. What size?"
        	elif(dialogAct.slot == "pizza"): # TODO
        		return "Sorry, I didn't get that. ...ground pizza..."
        	elif(dialogAct.slot == "name"):
        		return "Sorry, I didn't get that. Name?"
        	elif(dialogAct.slot == "number"):
        		return "Sorry, I didn't get that. Phone Number?"
        	elif(dialogAct.slot == "modality"):
        		return "Sorry, I didn't get that. Pick up or delivery?"
        	elif(dialogAct.slot == "address"):
        		return "Sorry, I didn't get that. Address?"
        	elif(dialogAct.slot == "order"): #TODo
        		return "Sorry, I didn't get that. ...ground order..."

        	else:
        		return "Not implemented yet"


        else:
            return "Not implemented yet"