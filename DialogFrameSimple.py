import json

class DialogFrameSimple:

    def __init__(self):
        self.FrameName = "DialogFrameSimple"
        # add whatever fields you want here
        # the things that are part of the IS are 
        # pizza type, crust, size, 
        # person (name & number), modality, address
        # self.pizza = Pizza()
        # self.name = None
        # self.number = None
        # self.modality = None
        # self.address = None
        # self.price = 0
        self.ground_pizza = False
        self.ground_order = False
        self.request = None
        self.order_status = None
        self.slots_filled = set()

    def update(self,ground_pizza,ground_order,request,slots):
        # self.pizza = Pizza(specialty_type=slots[0],crust=slots[1],size=slots[2])
        # self.name = slots[3]
        # self.number = slots[4]
        # self.modality = slots[5]
        # self.address = slots[6]
        self.ground_pizza = False if not ground_pizza else True # 7
        self.ground_order = False if not ground_order else True # 8
        self.request = request #slots[5] # [9]
        self.slots_filled = self.slots_filled.union(slots)
        # self._consolidate_user_data(DB)

