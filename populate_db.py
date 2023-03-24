import json

data = {}
data['users'] = [
    {'name':'peter','number':'123-456-7890','address':'123 Street',
     'preferred':{'pizza_type': '4 cheese',
                   'crust':'regular',
                   'size':'medium',
                   'toppings':['mozzarella','cheddar','swiss','provelone']
                    }},
    {'name':'paul','number':'123-567-8904','address':'123 Ave',
     'preferred':{'pizza_type': 'pepperoni',
                   'crust':'gluten-free',
                   'size':'large',
                   'toppings':['mozzarella','pepperoni']
                    }},
    {'name':'mary','number':'123-678-9045','address':'123 Blvd',
     'preferred':{'pizza_type': 'vegan',
                   'crust':'thin',
                   'size':'small',
                   'toppings':['green peppers','red onions','mushrooms','black olives']
                    }}]
data['defaults'] = [
    {'name':'basic', 'toppings':[]},
    {'name':'hawaiian', 'toppings':['pineapple','ham','mozzarella']},
    {'name':'meat lovers', 'toppings':['mozzarella','pepperoni','ham','bacon','sausage']},
    {'name':'4 cheese', 'toppings':['mozzarella','cheddar','swiss','provolone']},
    {'name':'pepperoni', 'toppings':['mozzarella','pepperoni']},
    {'name':'veggie supreme', 'toppings':['mozzarella','green peppers','red onions','mushrooms','black olives']},
    {'name':'vegan', 'toppings':['green peppers','red onions','mushrooms','black olives']}]
data['toppings'] = [
    {'name':'mozzarella','type':'cheese','price':1.5},
    {'name':'cheddar','type':'cheese','price':1.5},
    {'name':'swiss','type':'cheese','price':1.5},
    {'name':'provelone','type':'cheese','price':1.5},
    {'name':'pineapple','type':'veggie','price':2},
    {'name':'green peppers','type':'veggie','price':2},
    {'name':'pineapple','type':'veggie','price':2},
    {'name':'red onions','type':'veggie','price':2},
    {'name':'mushrooms','type':'veggie','price':2},
    {'name':'black olives','type':'veggie','price':2},
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
    {'name':'deep dish','size':'small','price':12},
    {'name':'deep dish','size':'medium','price':14},
    {'name':'deep dish','size':'large','price':16},
    {'name':'gluten-free','size':'small','price':15},
    {'name':'gluten-free','size':'medium','price':18},
    {'name':'gluten-free','size':'large','price':21}]
data['open_orders']= [
    {'name':'peter','confirmation_number':'00001',
        'modality':'pick-up','status':'cancelled'},
    {'name':'peter','confirmation_number':'00002',
        'modality':'pick-up','status':'baking'},
    {'name':'paul','confirmation_number':'00003',
        'modality':'delivery','status':'ready'}]
data['modality'] = {'pick-up':0,'delivery':3},
data['order_idx'] = 4

with open('db.json', 'w') as outfile:
    json.dump(data, outfile,indent=3)