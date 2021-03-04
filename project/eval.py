from numpy import nan

def accuracy(y,y_pred):
	denom = 0
	num = 0
	for utt,uttp in zip(y,y_pred):
		for slot,slotp in zip(utt,uttp):
			if slot == slotp:
				num +=1
			denom+=1
	return num/denom, denom

def class_accuracy(y,y_pred,target_slot):
	# return the class accuracy and class size for a slot
	denom  = 0
	num = 0 
	for utt,uttp in zip(y,y_pred):
		for slot,slotp in zip(utt,uttp):
			if slot == target_slot:
				if slot == slotp:
					num +=1
				denom+=1
	if denom == 0:
		return nan, 0
	else:
		return num/denom, denom