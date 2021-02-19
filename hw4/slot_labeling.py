import argparse
import nltk
import numpy as np
import pandas as pd
import random
import re
import sklearn_crfsuite
from sklearn_crfsuite import scorers
from sklearn_crfsuite import metrics
from sklearn.metrics import accuracy_score
from nltk.tokenize import word_tokenize
from bs4 import BeautifulSoup

''' take as input the tsv files created in homework 3
output similar files with predicted slot tags and true intents for 
intent classification

hyperparameters:
n - the number of ngrams
lexical cateoriges - user defined word clusters 
	for intent or slot classification
noise - the probbaility with whicch to mask words in training to simulate
	ASR errors

first modified 16 february 2021
last modified 19 feburary 2021
sara ng

'''

def preprocess_data(train,noise=0):
	# take in training data and read it into dataframe
	with open(train,'r') as f:
		data = pd.read_csv(f,sep='\t')

	# the clean text and unencoded slot tags and postags and ngrams
	text_and_tags = data.apply(lambda x: tokenize_and_tag(x,noise),
			axis='columns', result_type='expand')
	data = pd.concat([data,text_and_tags],axis='columns')
	data = data.rename(columns = {0:'tokenized',1:'slots',2:'ngrams',3:'pos'})
	data['lexcats'] = data.tokenized.apply(lambda x: define_lexical_cateories(x))
	all_utterances = []
	num_lexcats = data.lexcats.loc[0].shape[1]

	# make dictionaries of the kind sklearn likes 
	for utterance_idx in range(data.shape[0]):
		utt = data.loc[utterance_idx]
		words_in_utt =[]
		for word_idx in range(2,utt.lexcats.shape[0]+2):
			word = { 'word':utt.tokenized[word_idx], # word
					't-2':utt.tokenized[word_idx-2], # word @ t-2
					't-1':utt.tokenized[word_idx-1], # word @ t-1
					'pos':utt.pos[word_idx]} # pos
			# lexical categories
			for i in range(num_lexcats):
				word.update({'lexcat_{}'.format(i):bool(utt.lexcats[word_idx-2,i])})
			# ngrams
			word.update({'bigram':' '.join([word['word'],word['t-1']]),
						'trigram':' '.join([word['word'],word['t-1'],word['t-2']])})
			words_in_utt.append(word)
		all_utterances.append(words_in_utt)
	return all_utterances ,data.slots.to_list(), data.Intent.to_list()

def tokenize_and_tag(x,noise):
	# pull out the tokens, slot tags, ngrams, and pos tags
	soup = BeautifulSoup(x.Sentence.lower(),'html.parser')
	tokenized = []
	slottags =[]
	for tag in soup.contents:
		tagname = tag.name if tag.name else 'O'
		try:
			tok = word_tokenize(tag.text)
		except AttributeError:
			tok = word_tokenize(tag)
		for word in tok:
			slottags.append(tagname)
			if random.random() < noise:
				tokenized.append('******')
			else:
				tokenized.append(word)
	postags= ['BOS']*2+[t[1] for t in nltk.pos_tag(tokenized)]
	whitespace_tokenized = ['<S>']*2+tokenized
	ngrams = [' '.join(whitespace_tokenized[i:i+3]) for i in range(len(tokenized))]
	return whitespace_tokenized, slottags, ngrams,postags

def define_lexical_cateories(x):
	# x is a list, tokenized sentence
	# define membership in lexical 
	lists = [["need", "let", "'s", "go", "with", "can", "could", "get"],
		["get", "or", "soon", "possible", "'ll", "be",],
		["card", "code", "expiration", "number", "date", "security"],
		["under", "card", "number", "name", "street"],
		["cola", "soda", "root", "beer", "ceasar", "salad", "side"],
		['cheddar','swiss','provolone','pineapple','greenpeppers','onions',
				'mushrooms','olives','pepperoni','ham','bacon','sausage'],
		["how", "long", "when", "where", "'s", "ready", "order"],
		["yes", "yeah", "yep", "absolutely", "right", "great", "okay", "mhm", 
				"amazing", "perfect"],
		["no", "nope"],
		["bye", "too", "bye-bye", "peace"],
		["all", "that" "'ll", "will", "should", "it"],
		["hello", "hi", "hi!", "hey", "how", "'s" "going", "ring"],
		["i","have", "want", "like", "may", "can", "need", "let", "'s", "get", 
				"could", "order"],
		["change"],
		["update", "my", "preferred", "change"],
		["favorite", "frequent", "usual", "preferred", "common", "previous", 
				"recent", "my", "most"],
		["without", "off", "take"],
		["have", "recommend"],
		["how much", "cost", "price", "prices", "money"],
		["drink", "what", "kind", "kinds", "do"],
		["place", "order", "like", "hey", "pizza"],
		["thank", "thanks"],
		["rather", "rather", "actually", "different", "no", "prefer", "second", 
			"sthought"],
		["actually", "hoping", "change"],
		["sorry"],
		["it", "'s", "for", "wait", "actually", "no", "sorry"]]

	matrices=  []
	length =len(lists)
	for word in x[2:]:
		value_matrix = [0]*length
		for i,l in enumerate(lists):
			if word in l:
				value_matrix[i]=1
		matrices.append(value_matrix)
	return np.vstack(matrices)

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
		return np.nan, 0
	else:
		return num/denom, denom

def main():

	###################
	# hyperparameters #
	###################

	parser = argparse.ArgumentParser(description='slot classification params')
	parser.add_argument('-n','--noise',type=float,default=0.0,
			help='dropout rate to use in training')
	args = parser.parse_args()

	#################
	# preprocessing #
	#################

	train_path = 'data_for_slot/hw3_train.txt'
	evaluation_paths = {'heldout': 'data_for_slot/hw3_test.txt',
						'DATA0': 'data_for_slot/data0.txt',
						'DATA5': 'data_for_slot/data5.txt',
						'DATA6': 'data_for_slot/data6.txt'}
	# adjust the noise in training
	X, y, train_intents = preprocess_data(train_path,noise=args.noise)
	test_data_X = {}
	test_data_y = {}
	test_data_intent = {}
	for k,v in evaluation_paths.items():
		print('processing {}...'.format(k))
		test_data_X[k],test_data_y[k], test_data_intent[k]=preprocess_data(v)
	evaluation_paths.update({'train':'hw_train.txt'})
	test_data_X.update({'train':X})
	test_data_y.update({'train':y})
	test_data_intent.update({'train':train_intents})
	############
	# training #
	############

	crf = sklearn_crfsuite.CRF()
	crf.fit(X, y)

	##############
	# evaluation #
	##############

	predictions = {'train':{},'heldout':{},'DATA0':{},'DATA5':{},'DATA6':{}}
	predictions_by_class = {'train':{},'heldout':{},'DATA0':{},'DATA5':{},'DATA6':{}}
	frames_by_class = {'train':{},'heldout':{},'DATA0':{},'DATA5':{},'DATA6':{}}
	all_predicted_tags = {'train':{},'heldout':{},'DATA0':{},'DATA5':{},'DATA6':{}}
	labels = list(crf.classes_)

	for k,v in test_data_X.items():
		predicted = crf.predict(v)
		y_test = test_data_y[k]
		# get a total acccuracy and f1
		predictions[k]['f1'] = metrics.flat_f1_score(y_test, predicted,
										average='weighted', 
										labels=labels)
		predictions[k]['acc'], predictions[k]['n'] = accuracy(y_test,predicted)
		# also get accuracy and f1 by slot type
		for label in labels:
			predictions_by_class[k][label] =  (metrics.flat_f1_score(y_test,
					predicted,average='weighted',labels=[label]),
					*class_accuracy(y_test,predicted,label))
		all_predicted_tags[k]=predicted
		frames_by_class[k] = pd.DataFrame.from_dict(
				predictions_by_class[k],columns=['f1','acc','n'],orient='index')
	metrics_by_data = pd.DataFrame.from_dict(predictions,
			columns=['f1','acc','n'],orient='index')

	############
	# analysis #
	############

	for k,v in predictions.items():
		text = 'TEST RESULTS\n\nOVERALL\n\n'
		text += str(metrics_by_data.loc[k:k])
		text += '\n\nBY CLASS\n\n'
		text += str(frames_by_class[k][frames_by_class[k].n>0])
		with open('slot_results/slot_tagging_eval_{}_n_{}.txt'.format(k,args.noise),'w') as f:
			f.write(text)

	#######################
	# ASR errors readable #
	#######################

	data = [' '.join([re.sub(r',','',str((a['word'],b,c))) for a,b,c in zip(c,d,e)]) \
			for c,d,e in zip(test_data_X['DATA6'],
			test_data_y['DATA6'],all_predicted_tags['DATA6'])]

	with open('slot_results/analyze_data6_n_{}.txt'.format(args.noise),'w') as f:
		f.write('\n'.join(data))


	##########################################
	# prepare data for intent classification #
	##########################################

	# push tokenized text with labels into file
	# there is ambiguity about tag ends and starts, 
	# which we will handle greedily
	for dataset,intents in test_data_intent.items():
		# get the taggeed version of each utterance based on the prediction
		full_text = ['Intent\tSentence']
		for i,intent in enumerate(intents):
			wordlist = [a['word'] for a in test_data_X[dataset][i]]
			taglist = all_predicted_tags[dataset][i]
			last_tag = ''
			text = []
			opened_tag = False
			# reform the tetxt
			for j,(word,tag) in enumerate(zip(wordlist,taglist)):
				if tag != last_tag:
					if j > 0 and last_tag!='O':
						text.append('</'+last_tag+'>')
						opened_tag = False
					if tag != 'O':
						text.append('<'+tag+'>')
						opened_tag = True
					last_tag = tag
				text.append(word)
			if opened_tag:
				text.append('</'+last_tag+'>')
			full_text.append('{}\t{}'.format(intent,' '.join(text)))
		with open('data_for_intent/{}.txt'.format(dataset),'w') as f:
			f.write('\n'.join(full_text))
		
if __name__ == "__main__":
	main()
