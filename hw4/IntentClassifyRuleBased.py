import sys, re
from NLURuleBased import NLURuleBased
import ipdb
from bs4 import BeautifulSoup
from sklearn.metrics import f1_score
from sklearn_crfsuite.metrics import flat_f1_score
from nltk.tokenize import word_tokenize
from numpy import nan

def get_data_from_annotated_file(data_file, annotated_data_file):
	labels = []
	instances = []
	gold_annotations = []
	slots = []

	with open(data_file) as df:
		data_lines = df.readlines()[1:]

	with open(annotated_data_file) as adf:
		annotated_data_lines = adf.readlines()[1:] 

	for i in range(len(data_lines)):
		data_line = data_lines[i]
		annotated_data_line = annotated_data_lines[i]

		
		_, _, instance = (' '.join(data_line.split())).split(" ", 2)
		instance = instance.rstrip()

		label = annotated_data_line.split()[0]
		gold_annotation = annotated_data_line.split("\t", 1)[1]
		soup = BeautifulSoup(gold_annotation,'html.parser')
		slottags =[]
		for tag in soup.contents: 
			tagname = tag.name if tag.name else 'O' 
			try: 
				tok = word_tokenize(tag.text.rstrip())
			except AttributeError: 
				tok = word_tokenize(tag.rstrip())
			slottags += [tagname for word in tok if word] #for word in tok:

		slots.append(slottags)


		labels.append(label)
		instances.append(instance)
		gold_annotations.append(gold_annotation)

	return labels, instances, gold_annotations,slots

def get_data(data_file):
	labels = []
	instances = []

	with open(data_file) as df:
		data_lines = df.readlines()[1:]

	for line in data_lines:
		label, instance = line.split('\t')
		instance = instance.rstrip()

		labels.append(label)
		instances.append(instance)

	return labels, instances


def annotate_data0():
	data0file = "shared-filtered"
	with open(data0file) as d0f:
		d0lines = d0f.readlines()
	for line in d0lines:
		annotation = NLU.parse(line)
		print(annotation)
		NLU.printSemanticFrame()
		NLU.clear_slots()

def annotate_data(NLU, data_file, gold_file):
	annotations = []
	pred_labels = []

	true_labels, instances, gold_annotations, gold_slots = get_data_from_annotated_file(data_file, gold_file)

	pred_labels = []
	annotations = []
	pred_slots = []
	for i,instance in enumerate(instances):
		annotation = NLU.parse(instance)
		soup = BeautifulSoup(annotation,'html.parser')
		pred_tags =[]
		for tag in soup.contents: 
			tagname = tag.name if tag.name else 'O' 
			try: 
				tok = word_tokenize(tag.text.rstrip())
			except AttributeError: 
				tok = word_tokenize(tag.rstrip())
			pred_tags += [tagname for word in tok if word]
		pred_slots.append(pred_tags)
		annotations.append(annotation)
		pred_label = NLU.SemanticFrame.Intent.name
		pred_labels.append(pred_label)

	return annotations, pred_labels, true_labels, instances, gold_annotations, pred_slots, gold_slots

def accuracy(pred_labels, true_labels):
	correct =  sum(pred_labels[i] == true_labels[i] for i in range(len(pred_labels)))
	total = len(pred_labels)
	return float(correct) / float(total)


def class_accuracy_slot(y,y_pred,target_slot):
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

def class_accuracy_intent(y,y_pred,target_intent):
	# return the class accuracy and class size for a slot
	denom  = 0
	num = 0 
	for slot,slotp in zip(y,y_pred):
		if slot == target_intent:
			if slot == slotp:
				num +=1
			denom+=1
	if denom == 0:
		return nan, 0
	else:
		return num/denom, denom



def main():
	NLU = NLURuleBased()
	data_file = sys.argv[1]
	gold_file = sys.argv[2]

	annotations, pred_labels, true_labels, instances, gold_annotations, slots, gold_slots = annotate_data(NLU, data_file, gold_file)

	# Intent
	acc = accuracy(pred_labels, true_labels)
	f1 = f1_score(pred_labels, true_labels, average="weighted")

	# Slot
	slot_acc = accuracy([t for s in slots for t in s], [t for s in gold_slots for t in s])
	slot_f1 = flat_f1_score(slots,gold_slots,average='weighted')

	for i in range(len(true_labels)):
		print("instance: {}\tpred label: {}\ttrue label {}".format(i, pred_labels[i], true_labels[i]))
		print("annotation: {}\n".format(annotations[i]))
		print("gold_annotation {}\n".format(gold_annotations[i]))

	print("intent accuracy on data: ", acc)
	print("intent f1 score on data: ", f1)
	print("slot accuracy on data: ", slot_acc)
	print("slot f1 on data: ", slot_f1)
	
	print("BY INTENT")

	print('intent\taccuracy\tn')
	for intent in set(true_labels):
		print('{}\t{:.6f}\t{}'.format(intent,*class_accuracy_intent(true_labels,pred_labels,intent)))


	print("BY SLOT")
	print('slot\taccuracy\tn')
	for slot in set([t for s in gold_slots for t in s]):
		print('{}\t{:.6f}\t{}'.format(slot,*class_accuracy_slot(gold_slots,slots,slot)))
	print("Rule based NLU - enter query:")

	while(True):
		inputStr = input("> ")
		if (inputStr == "Quit"):
			break
		annotation = NLU.parse(inputStr)
		#ipdb.set_trace()
		print("Predicted Intent: ", NLU.SemanticFrame.Intent.name)
		print("Predicted Slot annotation: ", annotation)
		NLU.clear_slots()

if __name__ == '__main__':
	main()