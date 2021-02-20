import sys, ipdb, re
from nltk import word_tokenize
from nltk.util import ngrams
from sklearn.svm import SVC
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import f1_score, accuracy_score
from collections import Counter
import numpy as np

###################### HELPER FUNCTIONS ######################
def load_hand_picked():
	hand_picked = []
	with open("hand_picked_class_words.txt") as f:
		lines = f.readlines()

	for line in lines:
		line = line.rstrip().strip()
		if line and line[0] == '\"':
			hand_picked.append(line[1:-1])

	return sorted(list(set(hand_picked)))

def get_hand_picked_vectors(instances, all_hand_picked):
	N = len(all_hand_picked)

	hand_picked_matrix = []
	for instance in instances:
		hand_picked_vector = [0] * N
		for i, hp in enumerate(all_hand_picked):
			if hp in instance:
				#ipdb.set_trace()
				hand_picked_vector[i] = 1

		hand_picked_matrix.append(hand_picked_vector)
	np_hand_picked_matrix = np.array(hand_picked_matrix)
	return np_hand_picked_matrix

	slot_matrix = []
	for instance in instances:
		slots = list(set(re.findall(r"<\/(.*?)>", instance)))

		slot_vector = [0] * N
		for i in range(N):
			if all_slots[i] in slots:
				slot_vector[i] = 1

		slot_matrix.append(slot_vector)

	np_slot_matrix = np.array(slot_matrix)
	return np_slot_matrix

def get_slot_vectors(instances, all_slots):
	N = len(all_slots)
	slot_matrix = []
	for instance in instances:
		slots = list(set(re.findall(r"<\/(.*?)>", instance)))

		slot_vector = [0] * N
		for i in range(N):
			if all_slots[i] in slots:
				slot_vector[i] = 1

		slot_matrix.append(slot_vector)

	np_slot_matrix = np.array(slot_matrix)
	return np_slot_matrix

def get_all_slots(instances):
	all_slots = set()
	for instance in instances:
		all_slots |= set(re.findall(r"<\/(.*?)>", instance))

	return list(all_slots)

def get_bigrams(instances):
	all_bigrams = set()
	bigrams = []

	for instance in instances:
		tokens = re.split(' ', instance)
		bg = list(ngrams(tokens, 2))

		bigrams.append(Counter(bg)) 
		all_bigrams |= set(bg)

	return all_bigrams, bigrams

def get_trigrams(instances):
	all_trigrams = Counter()
	trigrams = []

	for instance in instances:
		tokens = re.split(' ', instance)
		tg = list(ngrams(tokens, 3))
		tgCounts = Counter(tg)

		trigrams.append(tgCounts)
		all_trigrams += tgCounts

	return all_trigrams, trigrams

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


###################### TEST ######################
def test_on_model(X_test, Y_test, model, model_name):
	Y_pred = model.predict(X_test)

	for i in range(len(Y_test)):
		print("Instance: {}\tPredicted label: {}\tTrue label: {}".format(i, Y_pred[i], Y_test[i]))

	test_acc = accuracy_score(Y_test, Y_pred)
	print("test accuracy with {}: ".format(model_name, test_acc))

	test_f1 = f1_score(Y_test, Y_pred, average="micro")
	print("test f1 score with {}: ".format(model_name, test_f1))


def test(test_instances, Y_test, all_slots, all_hand_picked, vectorizer, model, model_name, test_data):
	print("Testing " + test_data + " on " + model_name + " model ")

	test_grams = vectorizer.transform(test_instances).toarray()
	test_slots = get_slot_vectors(test_instances, all_slots)
	test_hand_picked = get_hand_picked_vectors(test_instances, all_hand_picked)

	X_test1 = test_grams
	X_test2 = test_slots
	X_test3 = test_hand_picked
	X_test4 = np.hstack([test_slots, test_hand_picked, test_grams])
	X_test5 = np.hstack([test_slots, test_hand_picked])
	X_test6 = np.hstack([test_slots, test_grams])

	if model_name == "all":
		test_on_model(X_test1, Y_test, model[0], model_name)
		test_on_model(X_test2, Y_test, model[1], model_name)
		test_on_model(X_test3, Y_test, model[2], model_name)
		test_on_model(X_test4, Y_test, model[3], model_name)
		test_on_model(X_test5, Y_test, model[4], model_name)
		test_on_model(X_test6, Y_test, model[5], model_name)

	elif model_name == "ngrams":
		test_on_model(X_test1, Y_test, model[0], model_name)

	elif model_name == "slots":
		test_on_model(X_test2, Y_test, model[1], model_name)

	elif model_name == "hand_picked":
		test_on_model(X_test3, Y_test, model[2], model_name)

	elif model_name == "ngrams+slots+hand_picked":
		test_on_model(X_test4, Y_test, model[3], model_name)

	elif model_name == "slots+hand_picked":
		test_on_model(X_test5, Y_test, model[4], model_name)

	elif model_name == "slots+ngrams":
		test_on_model(X_test6, Y_test, model[5], model_name)

	else:
		test_on_model(X_test1, Y_test, model[0], model_name)


def main():

	###################### TRAINING MODEL ON DATA 1-4 ######################
	data_file_1 = "DATA1/group5.txt"
	data_file_2 = "DATA2/group5.txt"
	data_file_3 = "DATA3/group5.txt"
	data_file_4 = "DATA4/group5.txt"
	data_1_labels, data_1_instances = get_data(data_file_1)
	data_2_labels, data_2_instances = get_data(data_file_2)
	data_3_labels, data_3_instances = get_data(data_file_3)
	data_4_labels, data_4_instances = get_data(data_file_4)

	true_labels = data_1_labels + data_2_labels + data_3_labels + data_4_labels
	instances = data_1_instances + data_2_instances + data_3_instances + data_4_instances

	###################### TRAIN/DEV SPLIT ######################
	N = len(instances)
	SPLIT_POINT = 	int(N * (0.8))
	train_instances = instances[:SPLIT_POINT]
	dev_instances   = instances[SPLIT_POINT:]
	Y_train    	= true_labels[:SPLIT_POINT]
	Y_dev 		= true_labels[SPLIT_POINT:]

	###################### TRAINING FEATURES ######################
	# Get sets for all possible feature types (slots, hand picked lexica)
	all_slots = get_all_slots(instances)
	all_hand_picked = load_hand_picked()

	# Get ngrams (bigrams, trigrams) using CountVectorizer
	vectorizer = CountVectorizer(ngram_range=(2,3))
	train_grams = vectorizer.fit_transform(train_instances).toarray()
	dev_grams   = vectorizer.transform(dev_instances).toarray()

	# Get slot vectors
	train_slots = get_slot_vectors(train_instances, all_slots)
	dev_slots = get_slot_vectors(dev_instances, all_slots)

	# Get hand picked vectors	
	train_hand_picked = get_hand_picked_vectors(train_instances, all_hand_picked)
	dev_hand_picked = get_hand_picked_vectors(dev_instances, all_hand_picked)

	###################### FEATURE COMBINATIONS ######################
	X_train1 = train_grams
	X_dev1 = dev_grams

	X_train2 = train_slots
	X_dev2 = dev_slots

	X_train3 = train_hand_picked
	X_dev3 = dev_hand_picked

	X_train4 = np.hstack([train_slots, train_hand_picked, train_grams])
	X_dev4 = np.hstack([dev_slots, dev_hand_picked, dev_grams])

	X_train5 = np.hstack([train_slots, train_hand_picked])
	X_dev5 = np.hstack([dev_slots, dev_hand_picked])

	X_train6 = np.hstack([train_slots, train_grams])
	X_dev6 = np.hstack([dev_slots, dev_grams])

	###################### MODELS ######################
	model1 = SVC()
	model1.fit(X_train1, Y_train)

	model2 = SVC()
	model2.fit(X_train2, Y_train)

	model3 = SVC()
	model3.fit(X_train3, Y_train)

	model4 = SVC()
	model4.fit(X_train4, Y_train)

	model5 = SVC()
	model5.fit(X_train5, Y_train)

	model6 = SVC()
	model6.fit(X_train6, Y_train)

	###################### Development Testing on heldout set ######################
	# acc1 = model1.score(X_dev1,Y_dev)
	# acc2 = model2.score(X_dev2,Y_dev)
	# acc3 = model3.score(X_dev3,Y_dev)
	# acc4 = model4.score(X_dev4,Y_dev)
	# acc5 = model5.score(X_dev5,Y_dev)
	# acc6 = model6.score(X_dev6,Y_dev)

	# print("dev accuracy with ngrams: ", acc1)
	# print("dev accuracy with slots: ", acc2)
	# print("dev accuracy with hand picked: ", acc3)
	# print("dev accuracy with all: ", acc4)
	# print("dev accuracy with slots + hand picked: ", acc5)
	# print("dev accuracy with slots + ngrams: ", acc6)

	###################### True Testing on DATA0, DATA5, DATA6 ######################
	# data_file_0 = "DATA0/DATA0.txt"
	# data_file_5 = "DATA5/DATA5.txt"
	# data_file_6 = "DATA6/DATA6.txt"

	# data_0_labels, data_0_instances = get_data(data_file_0)
	# data_5_labels, data_5_instances = get_data(data_file_5)
	# data_6_labels, data_6_instances = get_data(data_file_6)

	# test_instances0 = data_0_instances
	# test_instances1 = data_5_instances
	# test_instances2 = data_6_instances
	# test_instances3 = data_5_instances + data_6_instances
	# Y_test0 = data_0_labels
	# Y_test1 = data_5_labels
	# Y_test2 = data_6_labels
	# Y_test3 = data_5_labels + data_6_labels

	# test("data0", test_instances0, Y_test0, all_slots, all_hand_picked, vectorizer, model1, model2, model3, model4, model5, model6)
	# test("data5", test_instances1, Y_test1, all_slots, all_hand_picked, vectorizer, model1, model2, model3, model4, model5, model6)
	# test("data6", test_instances2, Y_test2, all_slots, all_hand_picked, vectorizer, model1, model2, model3, model4, model5, model6)
	# test("data5 & data6", test_instances3, Y_test3, all_slots, all_hand_picked, vectorizer, model1, model2, model3, model4, model5, model6)
	while (True):
		model_name = input("choose a model to test on (ngrams, slots, hand_picked, ngrams+slots+hand_picked, all)>")

		test_data = sys.argv[1]
		#model_name = sys.argv[2]
		models = [model1, model2, model3, model4, model5, model6]

		if test_data == "dev_set":
			Y_test = Y_dev
			test_instances = dev_instances
		else:
			Y_test, test_instances = get_data(test_data)

		test(test_instances, Y_test, all_slots, all_hand_picked, vectorizer, models, model_name, test_data)

if __name__ == '__main__':
	main()