import json

data = {}
data['users'] = [
    {'name':'Peter','number':'123-456-7890','address':'123 Street',
     'preferred':[{'crust':'regular',
                   'size':'medium',
                   'toppings':['mozzarella','cheddar','swiss','provelone']
                    }]},
    {'name':'Paul','number':'123-567-8904','address':'123 Ave',
     'preferred':[{'crust':'gluten_free',
                   'size':'large',
                   'toppings':['mozzarella','pepperoni']
                    }]},
    {'name':'Mary','number':'123-678-9045','address':'123 Blvd',
     'preferred':[{'crust':'thin',
                   'size':'small',
                   'toppings':['green_peppers','red_onions','mushrooms','black_olives']
                    }]}]
data['defaults'] = [
    {'name':'hawaiian', 'toppings':['pineapple','ham','mozzarella']},
    {'name':'meat_lovers', 'toppings':['mozzarella','pepperoni','ham','bacon','sausage']},
    {'name':'cheese', 'toppings':['mozzarella','cheddar','swiss','provolone']},
    {'name':'pepperoni', 'toppings':['mozzarella','pepperoni']},
    {'name':'veggie_supreme', 'toppings':['mozzarella','green_peppers','red_onions','mushrooms','black_olives']},
    {'name':'vegan', 'toppings':['green_peppers','red_onions','mushrooms','black_olives']}]
data['toppings'] = [
    {'name':'mozzarella','type':'cheese','price':1.5},
    {'name':'cheddar','type':'cheese','price':1.5},
    {'name':'swiss','type':'cheese','price':1.5},
    {'name':'provelone','type':'cheese','price':1.5},
    {'name':'pineapple','type':'veggie','price':2},
    {'name':'green_peppers','type':'veggie','price':2},
    {'name':'pineapple','type':'red_onions','price':2},
    {'name':'mushrooms','type':'veggie','price':2},
    {'name':'black_olives','type':'veggie','price':2},
    {'name':'pepperoni','type':'meat','price':2.5},
    {'name':'ham','type':'meat','price':2.5}, 
    {'name':'bacon','type':'meat','price':3}, 
    {'name':'sausage','type':'meat','price':3}]
data['crusts']=[
    {'name':'thin','size':'small','price':10},
    {'name':'thin','size':'medium','price':12},
    {'name':'thin','size':'large','price':14},
    {'name':'regular','size':'small','price':10},
    {'name':'regular','size':'medium','price':12},
    {'name':'regular','size':'large','price':14},
    {'name':'deep_dish','size':'small','price':12},
    {'name':'deep_dish','size':'medium','price':14},
    {'name':'deep_dish','size':'large','price':16},
    {'name':'gluten_free','size':'small','price':15},
    {'name':'gluten_free','size':'medium','price':18},
    {'name':'gluten_free','size':'large','price':21}]
data['open_orders']= [
    {'name':'Peter','confirmation_number':'00001','status':'cancelled'},
    {'name':'Peter','confirmation_number':'00002','status':'baking'},
    {'name':'Paul','confirmation_number':'00003','status':'ready'}]
data['modality'] = {'pickup':0,'delivery':3}
data['order_idx'] = 4

with open('db.txt', 'w') as outfile:
    json.dump(data, outfile)