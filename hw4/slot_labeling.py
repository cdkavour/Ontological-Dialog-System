import pdb
import nltk
import numpy as np
import pandas as pd
import sklearn_crfsuite
from sklearn_crfsuite import scorers
from sklearn_crfsuite import metrics
from sklearn.metrics import accuracy_score
from nltk.tokenize import word_tokenize
from bs4 import BeautifulSoup

''' take as input one of the tsv files created in homework 3
output vectors of the kind we need to do 
intent classification and slot labeling

hyperparameters:
n - the number of ngrams
lexical cateoriges - user defined word clusters 
	for intent or slot classification

first modified 16 february 2021
sara ng

'''

debug = False

def preprocess_data(train,enc_bin=None):
	n = 3
	# given training data, define the vector space
	# including OOVs in each position

	# take in training data and read it into dataframe
	with open(train,'r') as f:
		data = pd.read_csv(f,sep='\t')

	if debug:
		data = data[:10]

	# the clean text and unencoded slot tags and postags and ngrams
	text_and_tags = data.apply(lambda x: tokenize_and_tag(x,n), axis='columns', result_type='expand')
	data = pd.concat([data,text_and_tags],axis='columns')
	data = data.rename(columns = {0:'tokenized',1:'slots',2:'ngrams',3:'pos'})
	data['lexcats'] = data.tokenized.apply(lambda x: define_lexical_cateories(x,n))
	all_utterances = []
	num_lexcats = data.lexcats.loc[0].shape[1]
	# make dictionaries of the kind sklearn likes 
	for utterance_idx in range(data.shape[0]):
		utt_data = data.loc[utterance_idx]
		words_in_utt =[]
		for word_idx in range(2,utt_data.lexcats.shape[0]+2):
			word = { 'word':utt_data.tokenized[word_idx], # word
					't-2':utt_data.tokenized[word_idx-2], # word @ t-2
					't-1':utt_data.tokenized[word_idx-1], # word @ t-1
					'pos':utt_data.pos[word_idx]} # pos
			# lexical categories
			for i in range(num_lexcats):
				word.update({'lexcat_{}'.format(i):bool(utt_data.lexcats[word_idx-2,i])})
			# ngrams
			word.update({'bigram':' '.join([word['word'],word['t-1']]),
						'trigram':' '.join([word['word'],word['t-1'],word['t-2']])})
			words_in_utt.append(word)
		all_utterances.append(words_in_utt)
	return all_utterances ,data.slots.to_list(), data.Intent.to_list()

def tokenize_and_tag(x,n):
	# pull out the tokens, slot tags, ngrams, and pos tags 
	soup = BeautifulSoup(x.Sentence,'html.parser')
	to_tokenize = word_tokenize(soup.get_text())
	whitespace_tokenized = ['<S>']*(n-1)+to_tokenize
	postags= ['BOS']*(n-1)+[t[1] for t in nltk.pos_tag(to_tokenize)]
	slottags =[]#['O']*(n-1)
	for tag in soup.contents:
		tagname = tag.name if tag.name else 'O'
		try:
			tok = word_tokenize(tag.text)
		except AttributeError:
			tok = word_tokenize(tag)
		for word in tok:
			slottags.append(tagname)

	ngrams = [' '.join(whitespace_tokenized[i:i+n]) for i in range(len(to_tokenize))]
	return whitespace_tokenized, slottags, ngrams,postags

def define_lexical_cateories(x,n):
	# x is a tokenized thing 
	# define membership in lexical 
	lists = [['thanks','thank'],
			['help','please']]
	matrices=  []
	length =len(lists)
	for word in x[n-1:]:
		value_matrix = [0]*length
		for i,l in enumerate(lists):
			if word in l:
				value_matrix[i]=1
		matrices.append(value_matrix)
	return np.vstack(matrices)

def accuracy(y,y_pred,exclude_O=False):
	denom = 0
	num = 0
	for utt,uttp in zip(y,y_pred):
		for word,wordp in zip(utt,uttp):
			if exclude_O and word == 'O':
				continue
			elif word == wordp:
				num +=1
			denom+=1
	return num/denom

def main():

	# training

	train_data = 'DATA1/group5.txt'
	test_data = 'DATA5/part1_annotated.tsv'
	X_train,y_slots,y_intent = preprocess_data(train_data)
	X_test, y_slots_test, y_intent_test = preprocess_data(test_data)
	crf = sklearn_crfsuite.CRF()
	pdb.set_trace()
	crf.fit(X_train, y_slots)

	# evaluation

	y_pred = crf.predict(X_train)
	labels = list(crf.classes_)
	train_f1 = metrics.flat_f1_score(y_slots, y_pred,average='weighted', labels=labels)
	train_acc = accuracy(y_slots,y_pred)
	y_pred_test = crf.predict(X_test)
	test_f1 = metrics.flat_f1_score(y_slots_test, y_pred_test,average='weighted', labels=labels)
	test_acc = accuracy(y_slots_test,y_pred_test)
	labels.remove('O')
	train_f1 = metrics.flat_f1_score(y_slots, y_pred,average='weighted', labels=labels)
	test_f1 = metrics.flat_f1_score(y_slots_test, y_pred_test,average='weighted', labels=labels)



if __name__ == "__main__":
	main()
