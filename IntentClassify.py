import sys, ipdb, re
from nltk import word_tokenize
from nltk.util import ngrams
from sklearn.svm import SVC
from sklearn.feature_extraction.text import CountVectorizer
from collections import Counter
import numpy as np

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

def main():

	all_hand_picked = load_hand_picked()
	#ipdb.set_trace()

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
	#true_labels = data_1_labels
	#instances = data_1_instances

	# Train/Dev split
	N = len(instances)
	SPLIT_POINT = 	int(N * (0.8))
	train_instances = instances[:SPLIT_POINT]
	dev_instances   = instances[SPLIT_POINT:]
	Y_train    	= true_labels[:SPLIT_POINT]
	Y_dev 		= true_labels[SPLIT_POINT:]

	all_bigrams, _ = get_bigrams(instances)
	all_slots = get_all_slots(instances)

	# Train Features
	#_, train_bigrams = get_bigrams(train_instances)
	#_, train_trigrams = get_trigrams(train_instances)
	train_slots = get_slot_vectors(train_instances, all_slots)
	train_hand_picked = get_hand_picked_vectors(train_instances, all_hand_picked)

	# Dev Features
	#_, dev_bigrams = get_bigrams(dev_instances)
	#_, dev_trigrams = get_trigrams(dev_instances)
	dev_slots = get_slot_vectors(dev_instances, all_slots)
	dev_hand_picked = get_hand_picked_vectors(dev_instances, all_hand_picked)


	#ipdb.set_trace()

	# Convert bigrams to sparse array
	vectorizer = CountVectorizer(ngram_range=(2,3))


	train_grams = vectorizer.fit_transform(train_instances).toarray()
	dev_grams   = vectorizer.transform(dev_instances).toarray()
	#ipdb.set_trace()
	#X_train = train_slots
	#X_dev = dev_slots


	#X_train = train_hand_picked
	#X_dev = dev_hand_picked

	X_train = np.hstack([train_slots, train_hand_picked, train_grams])
	X_dev = np.hstack([dev_slots, dev_hand_picked, dev_grams])

	#ipdb.set_trace()


	model = SVC()
	model.fit(X_train, Y_train)
	Y_pred = list(model.predict(X_dev))
	#Y_diff = list(zip(Y_pred, Y_dev))
	acc = model.score(X_dev,Y_dev)
	print("accuracy: ", acc)

	#ipdb.set_trace()

if __name__ == '__main__':
	main()