from bs4 import BeautifulSoup
from bs4.element import Tag
from eval import *
from nltk import pos_tag
import argparse
import glob
import numpy as np
import pandas as pd
import sklearn_crfsuite

''' crf for refexp and referent tagging tasks

last modified 19 march, 2021
sara ng
'''

slots = ['address', 'beverage', 'cost', 'crust', 'modality', 'name', 'number', 
		'numeric', 'payment', 'pizza_type', 'quant', 'side', 'size', 'store', 
		'time', 'topping', 'topping_type']
labels = ['B','I','O']

def make_list_of_dicts(soup):
	# given one transcript, make a list of lexemes 
	words = ['[BOS]','[BOS]']
	word_dicts = []
	for span in soup.contents:
		# if we are in a tag, look for subtags
		if type(span) == Tag:
			for sub_span in span.children:
				tag = sub_span.name
				if type(sub_span) == Tag:
					span_words = pos_tag(list(filter(None,sub_span.text.lower().split(' '))))
				else:
					span_words = pos_tag(list(filter(None,sub_span.lower().split(' '))))
				for word,pos in span_words:
					word_dict = {'word':word,
								't-2':words[-2],
								't-1':words[-1],
								'bigram':' '.join([word,words[-1]]),
								'trigram':' '.join([word,words[-1],words[-2]]),
								'pos':pos}
					word_dict.update({slot:slot==tag for slot in slots})
					word_dicts.append(word_dict)
					words.append(word)

		# we are in a string
		else: 
			span_words = pos_tag(list(filter(None,span.lower().split(' '))))
			for word,pos in span_words:
				word_dict = {'word':word,
							't-2':words[-2],
							't-1':words[-1],
							'bigram':' '.join([word,words[-1]]),
							'trigram':' '.join([word,words[-1],words[-2]]),
							'pos':pos}
				word_dict.update({slot:False for slot in slots})
				word_dicts.append(word_dict)
				words.append(word)

	return word_dicts

def make_list_of_dicts_and_gold(soup):
	# given one transcript, make a list of lexemes 
	words = ['[BOS]','[BOS]']
	word_dicts = []
	gold = []
	for span in soup.contents:
		# if we are in a tag, look for subtags
		if type(span) == Tag:
			if span.name == 'refexp':
				gold += ['B']+['I']*(len(list(filter(None,span.text.lower().split(' '))))-1)
			else:
				gold += ['O']*len(list(filter(None,span.text.lower().split(' '))))
			for sub_span in span.children:
				tag = sub_span.name
				if type(sub_span) == Tag:
					span_words = pos_tag(list(filter(None,sub_span.text.lower().split(' '))))
				else:
					span_words = pos_tag(list(filter(None,sub_span.lower().split(' '))))
				for word,pos in span_words:
					word_dict = {'word':word,
								't-2':words[-2],
								't-1':words[-1],
								'bigram':' '.join([word,words[-1]]),
								'trigram':' '.join([word,words[-1],words[-2]]),
								'pos':pos}
					word_dict.update({slot:slot==tag for slot in slots})
					word_dicts.append(word_dict)
					words.append(word)

		# we are in a string
		else: 
			span_words = pos_tag(list(filter(None,span.lower().split(' '))))
			gold += ['O']*len(span_words)
			for word,pos in span_words:
				word_dict = {'word':word,
							't-2':words[-2],
							't-1':words[-1],
							'pos':pos}
				word_dict.update({slot:False for slot in slots})
				word_dicts.append(word_dict)
				words.append(word)

	return word_dicts,gold

def preprocess_data_partI(file,n):
	# the n here is for number of turns, is ignored
	with open(file,'r') as f:
		data = pd.read_csv(f,sep='\t')
	data[['input','gold']] = pd.DataFrame(data.Transcript.apply(lambda x:make_list_of_dicts_and_gold(BeautifulSoup(x,'html.parser'))).tolist())
	return data.input.tolist(),data.gold.tolist()

def preprocess_data_partII(file,n):
	with open(file,'r') as f:
		data = pd.read_csv(f,sep='\t')
	grouped = data.groupby(['Conversation'])
	titles = grouped.groups.keys()
	group_dict = {title:grouped.get_group(title) for title in titles}
	gold = []
	input_features = []
	# for each conversation in this file
	for title,dataframe in group_dict.items():
		transcripts = list(dataframe.Transcript.values)
		# for each transcription
		for idx,transcript in enumerate(transcripts):
			soup = BeautifulSoup(transcript,'html.parser')
			history_soup = BeautifulSoup(' '.join(transcripts[max(0,-n+idx):idx]),'html.parser')
			# for each tag span in the transcription
			for idx2, tag in enumerate(soup.contents):
				if tag.name == 'refexp':
					# once you find one, pull the history
					this_history = BeautifulSoup(' '.join([str(a) for a in history_soup.contents+soup.contents[:idx2]]),'html.parser')
					gold_labels = []
					for span in this_history.contents[::-1]:
						try:
							words = [s for s in span.text.lower().split(' ') if s]
						except AttributeError:
							words = [s for s in span.lower().split(' ') if s]
						if span.name == 'ref' and span.attrs['id'] == tag.attrs['id']:
							gold_labels += ['I']*(len(words)-1)+['B']
						else:
							gold_labels += ['O']*len(words)
					gold.append(gold_labels[::-1])
					input_features.append(make_list_of_dicts(this_history))
	return input_features,gold

def train(path,n,preprocessor):
	X_train = []
	y_train = []
	for file in glob.glob(path):
		X_t,y_t = preprocessor(file,n)
		X_train+=X_t
		y_train+=y_t
	crf = sklearn_crfsuite.CRF()
	crf.fit(X_train, y_train)
	eval_data('train',crf,n,X_train,y_train)
	return crf

def eval_data(name,model,n,X,y):
	print('\n~~~~~{} data, turn history size n = {}~~~~~'.format(name,n))
	pred = model.predict(X)
	acc= accuracy(y,pred)
	f1 = sklearn_crfsuite.metrics.flat_f1_score(y, pred,average='weighted', labels=labels)
	print('{} overall accuracy = {:.2f}'.format(name,acc[0]*100))
	print('{} overall f1 = {:.5f}'.format(name,f1))
	for label in labels:
		label_acc = class_accuracy(y,pred,label)
		label_f1 = sklearn_crfsuite.metrics.flat_f1_score(y,pred,average='weighted',labels=[label])
		print('Label "{}" n = {}'.format(label,label_acc[1]))
		print('{} accuracy on "{}" tokens = {:.2f}'.format(name,label,label_acc[0]*100))
		print('{} f1 on "{}" tokens = {:.5f}'.format(name,label,label_f1))

def load_test(path,n,preprocessor):
	X_test = []
	y_test = []
	for file in glob.glob(path):
		X_t,y_t = preprocessor(file,n)
		X_test+=X_t
		y_test+=y_t	
	return X_test,y_test

def partI(train_data_path,test_data_path):
	model = train(train_data_path,args.num_turns,preprocess_data_partI)
	X_test,y_test = load_test(test_data_path,args.num_turns,preprocess_data_partI)
	eval_data('test',model,args.num_turns,X_test,y_test)

def partII(train_data_path,test_data_path):
	# train model
	model = train(train_data_path,args.num_turns,preprocess_data_partII)

	# eval test data
	X_test, y_test = load_test(test_data_path,args.num_turns,preprocess_data_partII)
	eval_data('test',model,args.num_turns,X_test,y_test)

def main():
	global args
	parser = argparse.ArgumentParser(description='refexp classification params')
	parser.add_argument('-n','--num_turns',type=int,default=6,
			help='number of turns (excluding current) to use as history')
	args = parser.parse_args()

	# load in all of the files
	train_data_path = 'data/data4_annotated_for_ref/train/*.tsv'
	test_data_path = 'data/data4_annotated_for_ref/*.tsv'
	print('~~~~~~~predicting referring expressions~~~~~~~')
	partI(train_data_path,test_data_path)
	print('~~~~~~~predicting referents~~~~~~~')
	partII(train_data_path,test_data_path)

if __name__ == "__main__":
	main()
