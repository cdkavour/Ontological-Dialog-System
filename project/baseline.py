from bs4 import BeautifulSoup
from bs4.element import NavigableString
from eval import *
from sklearn_crfsuite import metrics
import ipdb
import argparse
import glob
import pandas as pd

''' baseline for refexp tagging task
last modified 19 march 2021
sara ng
'''
def get_refexp_words(train_data_path):
	'''get a wordlist of refexp items from the training data to use as a baseline in part I'''
	words = set()
	for file in glob.glob(train_data_path):
		with open(file,'r') as f:
			data = pd.read_csv(f,sep='\t')
		transcripts = ' '.join(data.Transcript.tolist())
		soup = BeautifulSoup(transcripts,'html.parser')
		spans = soup('refexp')
		words = words.union(set([word for l in [list(filter(None,span.text.lower().split(' '))) for span in spans] for word in l]))
	return words

def run_data_partI(name,path,wordlist):
	gold = []
	pred = []
	for file in glob.glob(path):
		with open(file,'r') as f:
			data = pd.read_csv(f,sep='\t')
		data[['gold','pred']] = pd.DataFrame(data.Transcript.apply(lambda x:make_gold_and_pred(BeautifulSoup(x,'html.parser'),wordlist)).tolist())
		# import pdb;pdb.set_trace()
		gold += data.gold.tolist()
		pred += data.pred.tolist()
	labels = ['B','I','O']
	acc= accuracy(gold,pred)
	f1 = metrics.flat_f1_score(gold, pred,average='weighted', labels=labels)
	print('\n~~~~ {} set ~~~~~'.format(name))
	print('{} overall accuracy = {:.2f}'.format(name,acc[0]*100))
	print('{} overall f1 = {:.5f}'.format(name,f1))
	for label in labels:
		label_acc = class_accuracy(gold,pred,label)
		label_f1 = metrics.flat_f1_score(gold,pred,average='weighted',labels=[label])
		print('Label "{}" n = {}'.format(label,label_acc[1]))
		print('{} accuracy on "{}" tokens = {:.2f}'.format(name,label,label_acc[0]*100))
		print('{} f1 on "{}" tokens = {:.5f}'.format(name,label,label_f1))

def make_gold_and_pred(soup,wordlist):
	'''called within run_data_partI to create gold data for a string based on the wordlist'''
	gold = []
	pred = []
	for tag in soup.contents:
		label = tag.name
		if type(tag) == NavigableString:
			words = list(filter(None,tag.lower().split(' ')))
			gold += ['O']*len(words)		
		else:	
			words = list(filter(None,tag.text.lower().split(' ')))
			if tag.name == 'refexp':
				gold += ['B']+['I']*(len(words)-1)
			else:
				gold += ['O']*len(words)
		for word in words:
			if word in wordlist:
				if len(pred) > 0 and pred[-1] in ['B','I']:
					pred.append('I')
				else:
					pred.append('B')
			else:
				pred.append('O')
	return gold,pred

def run_data_partII(name,path):
	gold = []
	pred = []
	for file in glob.glob(path):
		g,p = baseline_partII(file,args.num_turns)
		gold += g
		pred += p
	labels = ['B','I','O']
	acc= accuracy(gold,pred)
	f1 = metrics.flat_f1_score(gold, pred,average='weighted', labels=labels)
	print('\n~~~~ {} set ~~~~~'.format(name))
	print('{} overall accuracy = {:.2f}'.format(name,acc[0]*100))
	print('{} overall f1 = {:.5f}'.format(name,f1))
	for label in labels:
		label_acc = class_accuracy(gold,pred,label)
		label_f1 = metrics.flat_f1_score(gold,pred,average='weighted',labels=[label])
		print('Label "{}" n = {}'.format(label,label_acc[1]))
		print('{} accuracy on "{}" tokens = {:.2f}'.format(name,label,label_acc[0]*100))
		print('{} f1 on "{}" tokens = {:.5f}'.format(name,label,label_f1))

def baseline_partII(file,n):
	'''called within run_data_partII to extract refexp from the tsv
	and do slot-based simple prediction'''
	with open(file,'r') as f:
		data = pd.read_csv(f,sep='\t')
	grouped = data.groupby(['Conversation'])
	titles = grouped.groups.keys()
	group_dict = {title:grouped.get_group(title) for title in titles}
	gold = []
	pred = []
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
					baseline_labels = []
					baseline_met = False
					# all_words = []
					for span in this_history.contents[::-1]:
						try:
							words = [s for s in span.text.lower().split(' ') if s]
						except AttributeError:
							words = [s for s in span.lower().split(' ') if s]
						if span.name == 'ref' and span.attrs['id'] == tag.attrs['id']:
							gold_labels += ['I']*(len(words)-1)+['B']
						else:
							gold_labels += ['O']*len(words)
						if span.name and not baseline_met:
							baseline_labels += ['I']*(len(words)-1)+['B']
							baseline_met = True
						else:
							baseline_labels += ['O']*len(words)
					gold.append(gold_labels[::-1])
					pred.append(baseline_labels[::-1])

	return gold,pred

def main():
	global args
	parser = argparse.ArgumentParser(description='refexp classification params')
	parser.add_argument('-n','--num_turns',type=int,default=6,
			help='number of turns (excluding current) to use as history')
	args = parser.parse_args()

	# load in all of the files
	train_data_path = 'data/data4_annotated_for_ref/train/*.tsv'
	test_data_path = 'data/data4_annotated_for_ref/*.tsv'

	# create wordlist part I
	wordlist = get_refexp_words(train_data_path)
	
	# run baseline partI
	run_data_partI('train',train_data_path,wordlist)
	run_data_partI('test',test_data_path,wordlist)

	# run baseline part II
	run_data_partII('train', train_data_path)
	run_data_partII('test', test_data_path)

if __name__ == "__main__":
	main()
