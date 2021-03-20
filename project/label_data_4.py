from bs4 import BeautifulSoup
from collections import defaultdict as dd
from nltk.tokenize import word_tokenize
from sklearn.metrics import accuracy_score
from sklearn_crfsuite import CRF, metrics, scorers
import argparse
import nltk
import numpy as np
import pandas as pd
import random

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

def preprocess_test_data(test,noise=0.00):
	with open(test,'r') as f:
		data= pd.read_csv(f,sep='\t')
	tsv = data.copy()
	text_and_tags = data.apply(lambda x: tokenize_test(x),
			axis='columns', result_type='expand')
	data = pd.concat([data,text_and_tags],axis='columns')
	
	data = data.rename(columns = {0:'tokenized',1:'ngrams',2:'pos'})
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
	return all_utterances,tsv

def tokenize_test(x):
	# pull out the tokens, slot tags, ngrams, and pos tags
	tokenized = word_tokenize(x.Transcript)
	postags= ['BOS']*2+[t[1] for t in nltk.pos_tag(tokenized)]
	whitespace_tokenized = ['<S>']*2+tokenized
	ngrams = [' '.join(whitespace_tokenized[i:i+3]) for i in range(len(tokenized))]
	return whitespace_tokenized,ngrams,postags


def preprocess_data(train,noise=0.05):
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
	return all_utterances,data.slots.to_list(), data.Intent.to_list()

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
	return whitespace_tokenized, slottags,ngrams,postags

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
	parser.add_argument('-n','--noise',type=float,default=0.05,
			help='dropout rate to use in training')
	args = parser.parse_args()

	#################
	# preprocessing #
	#################

	train_path = 'data/unprocessed/hw3_train.txt'
	evaluation_paths = {'brown':'data/unprocessed/BrownSweeney.tsv',
						'dodds':'data/unprocessed/DoddsSanders.tsv',
						'drizin':'data/unprocessed/DrizinKeane.tsv',
						'durham':'data/unprocessed/DurhamGrant.tsv',
						'kavouras':'data/unprocessed/KavourasNg.tsv',
						'kodama':'data/unprocessed/KodamaSmith.tsv',
						'lin':'data/unprocessed/LinWu.tsv',
						'martins':'data/unprocessed/MartinsWen.tsv',
						'reid':'data/unprocessed/ReidRessler.tsv',
						'tseng':'data/unprocessed/TsengWang.tsv',}

	# adjust the noise in training
	X, y, train_intents = preprocess_data(train_path,noise=args.noise)
	test_data_X = {}
	test_data_frames = {}
	for k,v in evaluation_paths.items():
		test_data_X[k], test_data_frames[k]= preprocess_test_data(v)
	
	############
	# training #
	############

	crf = CRF()
	crf.fit(X, y)

	##############
	# evaluation #
	##############

	predictions = dd(dict)
	predictions_by_class = dd(dict)
	frames_by_class =dd(dict)
	all_predicted_tags = dd(dict)
	labels = list(crf.classes_)

	for k,v in test_data_X.items():
		predicted = crf.predict(v)

		# now print the predictions back

		##########################################
		# prepare data for intent classification #
		##########################################

		# push tokenized text with labels into file
		# there is ambiguity about tag ends and starts, 
		# which we will handle greedily
		# get the taggeed version of each utterance based on the prediction
		lines = []
		for i,taglist in enumerate(predicted):
			wordlist = [a['word'] for a in test_data_X[k][i]]
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
			lines.append(' '.join(text))
		test_data_frames[k].Transcript = lines
		test_data_frames[k].to_csv('data/data4_silver_annotations/{}.tsv'.format(k),sep='\t',index=False)
		
if __name__ == "__main__":
	main()
