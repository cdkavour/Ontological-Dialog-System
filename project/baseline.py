import argparse
import glob
import matplotlib.pyplot as plt
import pandas as pd
from bs4 import BeautifulSoup
from eval import *
from sklearn_crfsuite import metrics
import ipdb

''' baseline for refexp tagging task
last modified 28 feburary 2021
sara ng
'''

def baseline(file,n):
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

def run_data(name,path):
	gold = []
	pred = []
	for file in glob.glob(path):
		g,p = baseline(file,args.num_turns)
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

def main():
	global args
	parser = argparse.ArgumentParser(description='refexp classification params')
	parser.add_argument('-n','--num_turns',type=float,default=6,
			help='number of turns (excluding current) to use as history')
	args = parser.parse_args()

	# load in all of the files
	train_data_path = 'data/data4_annotated_for_ref/train/*.tsv'
	test_data_path = 'data/data4_annotated_for_ref/*.tsv'

	# run baseline
	run_data('train', train_data_path)
	run_data('test', test_data_path)

if __name__ == "__main__":
	main()
