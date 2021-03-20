from baseline import baseline
import glob
import pandas as pd
from bs4 import BeautifulSoup
import ipdb
from transformers import BertTokenizer, BertForTokenClassification, BertModel
import torch
import numpy as np
import sklearn_crfsuite
import torch.nn as nn
import torch.optim as optim
from sklearn.metrics import f1_score, accuracy_score
from sklearn.metrics import confusion_matrix
from time import time
import re
import argparse


# Feed-forward Neural Network
class MulticlassClassification(nn.Module):
    def __init__(self, num_feature, num_class):
        super(MulticlassClassification, self).__init__()
        
        # Hidden Layers
        self.layer_1 = nn.Linear(num_feature, 512)
        self.layer_2 = nn.Linear(512, 128)
        self.layer_3 = nn.Linear(128, 64)
        self.layer_out = nn.Linear(64, num_class) 
        
        # Activation fxn, Dropout, etc
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(p=0.2)
        self.batchnorm1 = nn.BatchNorm1d(512)
        self.batchnorm2 = nn.BatchNorm1d(128)
        self.batchnorm3 = nn.BatchNorm1d(64)
        
    # Forward function for forward pass through network
    def forward(self, x):
        x = self.layer_1(x)
        x = self.batchnorm1(x)
        x = self.relu(x)
        
        x = self.layer_2(x)
        x = self.batchnorm2(x)
        x = self.relu(x)
        x = self.dropout(x)
        
        x = self.layer_3(x)
        x = self.batchnorm3(x)
        x = self.relu(x)
        x = self.dropout(x)
        
        x = self.layer_out(x)
        
        return x

# Parse arguments
def parse_args():
	parser = argparse.ArgumentParser(description='refexp classification params for neural net')
	parser.add_argument('-n','--num_turns',type=int,default=6,
			help='number of turns (excluding current) to use as history')
	parser.add_argument('-E', '--num_epochs', type=int, default=10,
			help='number of epochs to use in training')
	parser.add_argument('-B', '--batch_size', type=int, default=32,
			help='batch size to use in training')
	parser.add_argument('-L', '--learning_rate', type=float, default=0.0007,
			help='batch size to use in training')
	parser.add_argument('-t', '--task', type=int, choices={1, 2}, default=1,
			help='Task to train for (1 for referring expression classification, 2 for referent classification)')
	args = parser.parse_args()
	return args

# Extract clean contents from an HTML tag
def cleanhtml(raw_html):
  cleanr = re.compile('<.*?>')
  cleantext = re.sub(cleanr, '', raw_html)
  return cleantext

# Return overall & per class accuracy
def multi_acc(y_pred, y_test):
	y_pred_softmax = torch.log_softmax(y_pred, dim = 1)
	_, y_pred_tags = torch.max(y_pred_softmax, dim = 1)    
    
	y_pred_np = np.array(y_pred_tags.detach())
	y_test_np = np.array(y_test.detach())

	acc = accuracy_score(y_test_np, y_pred_np)

	matrix = confusion_matrix(y_test_np, y_pred_np)
	acc_array = matrix.diagonal()/matrix.sum(axis=1)

	return acc, acc_array

# Return overall and per class f1 score
def f1(y_pred, y_test):
	y_pred_softmax = torch.log_softmax(y_pred, dim = 1)
	_, y_pred_tags = torch.max(y_pred_softmax, dim = 1)

	y_pred_np = np.array(y_pred_tags.detach())
	y_test_np = np.array(y_test.detach())

	f1_sc = f1_score(y_test_np, y_pred_np, labels=[0, 1, 2], average='weighted')
	f1_array = f1_score(y_test_np, y_pred_np, labels=[0, 1, 2], average=None)

	return f1_sc, f1_array

# Accuracy & F1 Score
def evaluate(y_pred, y_test):
	labels = torch.max(y_test, 1)[1]

	acc, acc_array = multi_acc(y_pred, labels)
	f1sc, f1_array = f1(y_pred, labels)

	return acc, f1sc, acc_array, f1_array

# Get one-hot vector representation of  B-I-O labels
def conv_bio_to_onehot(labels):
	length = len(labels)
	one_hot = torch.zeros([length, 3])
	for i in range(length):
		if labels[i] == 'B':
			one_hot[i][0] = 1
		elif labels[i] == 'I':
			one_hot[i][1] = 1
		elif labels[i] == 'O':
			one_hot[i][2] = 1

	return one_hot 

# Return refexp history & B-I-O tags for referrents (for task 2)
def get_refexp_history(file,n):
	with open(file,'r') as f:
		data = pd.read_csv(f,sep='\t')
	grouped = data.groupby(['Conversation'])
	titles = grouped.groups.keys()
	group_dict = {title:grouped.get_group(title) for title in titles}
	gold = []
	word = []
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
					words_list = []
					for span in this_history.contents[::-1]:
						try:
							words = [s for s in span.text.lower().split(' ') if s]
							words_list += words[::-1]
						except AttributeError:
							words = [s for s in span.lower().split(' ') if s]
							words_list += words[::-1]
						if span.name == 'ref' and span.attrs['id'] == tag.attrs['id']:
							gold_labels += ['I']*(len(words)-1)+['B']
						else:
							gold_labels += ['O']*len(words)

					word.append(words_list[::-1])
					gold.append(gold_labels[::-1])

	return gold, word

# Tokenize words for BERT & extend their labels accordingly
def get_bert_tokens_and_labels(goldlists, wordlists, tags, tokenizer):
	NUM_INPUTS = len(goldlists)

	bert_tokens = []
	gold_for_bert = []
	for i in range(NUM_INPUTS):
		g = goldlists[i]
		wlist = wordlists[i]

		w_bert = []
		g_ext  = []
		for j, w in enumerate(wlist):
			ids = tokenizer.encode(w, add_special_tokens=False)
			id_len = len(ids)

			w_bert.extend(ids)
			g_ext.extend(g[j] * id_len)

		bert_tokens.append(w_bert)
		gold_for_bert.append(g_ext)

	return bert_tokens, gold_for_bert

# Extract tagged B-I-O word level data for referring expressions
def get_tokens_for_refexp(file):
	with open(file,'r') as f:
		data = pd.read_csv(f,sep='\t')
	grouped = data.groupby(['Conversation'])
	titles = grouped.groups.keys()
	group_dict = {title:grouped.get_group(title) for title in titles}
	gold = []
	word = []
	# for each conversation in this file
	for title,dataframe in group_dict.items():
		transcripts = list(dataframe.Transcript.values)
		# for each transcription
		for idx,transcript in enumerate(transcripts):
			wordlist = []
			goldlist = []
			soup = BeautifulSoup(transcript,'html.parser')
			for idx2, tag in enumerate(soup.contents):
				tagwords = cleanhtml(str(tag)).split()
				for i, w in enumerate(tagwords):
					wordlist.append(w)
					if tag.name == 'refexp':
						if i == 0:
							goldlist += 'B'
						else:
							goldlist += 'I'
					else:
						goldlist += 'O'
				word.append(wordlist)
				gold.append(goldlist)
	return gold, word

# Process data for downstream use
# Returns word embeddings from BERT
def process_data(data_path, bs=32, task=2, n=6):
	goldlists = []
	wordlists = []
	for file in glob.glob(data_path):
		if task == 1:
			g, w = get_tokens_for_refexp(file)
		else:
			g, w = get_refexp_history(file,n)
		goldlists += g
		wordlists += w

	# Get list of bert-tokens for each context, and extend B-I-O labels to match
	tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
	bert_tokens, gold_for_bert = get_bert_tokens_and_labels(goldlists, wordlists, None, tokenizer)

	# Pad bert tokens to a max length
	N_INPUT_LISTS = len(bert_tokens)
	# Can tweak this max list length as a hyper parameter
	#max_list_len = max(len(bt) for bt in bert_tokens)
	attention_masks = []
	max_list_len = 62
	for i in range(N_INPUT_LISTS):
		# Add CLS and SEP tokens
		bert_tokens[i] = [101] + bert_tokens[i] + [102]
		gold_for_bert[i] = [0] + gold_for_bert[i] + [0]

		orig_num = len(bert_tokens[i])
		pad_num = max(0, max_list_len - len(bert_tokens[i]))

		# Add padding
		bert_tokens[i].extend([0] * pad_num)
		gold_for_bert[i].extend([0] * pad_num)

		# Chop to max len
		bert_tokens[i] = bert_tokens[i][:max_list_len]
		gold_for_bert[i] = gold_for_bert[i][:max_list_len]
		attention_mask = [1] * orig_num + [0] * pad_num
		attention_mask = attention_mask[:max_list_len]
		attention_masks.append(attention_mask)

	# Get tensors
	batch_size = len(bert_tokens)
	seq_len = len(bert_tokens[0])

	# 1 context per row
	bert_tokens_tensors = torch.zeros([batch_size, seq_len], dtype=torch.long)
	attn_masks_tensors = torch.zeros([batch_size, seq_len], dtype=torch.long)
	for i in range(batch_size):
		for j in range(seq_len):
			bert_tokens_tensors[i][j] = bert_tokens[i][j]
			attn_masks_tensors[i][j] = attention_masks[i][j]

	# all contexts 1 row
	# bert_tokens_tensors = torch.zeros([1, batch_size * seq_len], dtype=torch.long)
	# for i in range(0, batch_size):
	# 	for j in range(0, seq_len):
	# 		idx = (i * seq_len) + j
	# 		bert_tokens_tensors[0][idx] = bert_tokens[i][j]

	# Train BERT
	print("\nTRAINING BERT... MAY TAKE A WHILE...\n")
	t1 = time()
	model = BertForTokenClassification.from_pretrained('bert-base-uncased', output_hidden_states = True)
	with torch.no_grad():
		outputs = model(bert_tokens_tensors, attention_mask=attn_masks_tensors)
	t2 = time()
	print("\n\nBERT Training Time: {} Minutes\n\n".format((t2-t1) / 60))

	gold_for_bert_all = [tok for gtoken in gold_for_bert for tok in gtoken]
	attention_mask_all = [tok for atoken in attention_masks for tok in atoken]

	# Extract hidden states
	hidden_states = outputs[1]
	token_embeddings = torch.stack(hidden_states, dim=0)
	token_embeddings = token_embeddings.permute(1,2,3,0)
	token_embeddings = token_embeddings.reshape(batch_size*seq_len, 768, 13)
	token_embeddings = token_embeddings[:,:,-4:]
	token_embeddings = torch.sum(token_embeddings, axis=2)

	# Remove padded
	nonz = []
	for i in range(len(gold_for_bert_all)):
		if gold_for_bert_all[i] != 0:
			nonz.append(1)
		else:
			nonz.append(0)
	nonz = torch.ByteTensor(nonz)
	X = token_embeddings[nonz]
	Y = [g for g in gold_for_bert_all if g != 0]

	# Convert B-I-O labels to one-hot-vector
	Y = conv_bio_to_onehot(Y)

	# Make num instances divisible by batch size
	new_len = int(int(X.shape[0] / bs) * bs)
	X = X[:new_len]
	Y = Y[:new_len]

	# Return features & labels
	return X, Y

def main():
	# Parse hyper-parameter arguments
	args = parse_args()
	num_turns = args.num_turns
	task = args.task
	EPOCHS = args.num_epochs
	BATCH_SIZE = args.batch_size
	LEARNING_RATE = args.learning_rate

	# Process data -- pipelines our annotated data down to
	# word embeddings for classification
	train_data_path = 'data/data4_annotated_for_ref/train/*.tsv'
	if task == 1: # For task 1, use reduced training set
		train_data_path = 'data/data4_annotated_for_ref/train2/*.tsv'
	test_data_path = 'data/data4_annotated_for_ref/*.tsv'
	train_X, train_Y = process_data(train_data_path, task=task, n=num_turns)
	test_X, test_Y = process_data(test_data_path, task=task, n=num_turns)
	TRAIN_INSTANCES = train_X.shape[0]
	NUM_FEATURES = train_X.shape[1]
	NUM_CLASSES = 3

	# Instantiate NN
	model = MulticlassClassification(num_feature=NUM_FEATURES, num_class=NUM_CLASSES)
	criterion = nn.CrossEntropyLoss()
	optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)

	# Batches
	train_batches_X = torch.split(train_X, BATCH_SIZE, dim=0)
	train_batches_Y = torch.split(train_Y, BATCH_SIZE, dim=0)

	# TRAIN
	epoch_accs = [0] * EPOCHS
	epoch_f1s = [0] * EPOCHS

	epoch_accs_B = [0] * EPOCHS
	epoch_accs_I = [0] * EPOCHS
	epoch_accs_O = [0] * EPOCHS

	epoch_f1s_B = [0] * EPOCHS
	epoch_f1s_I = [0] * EPOCHS
	epoch_f1s_O = [0] * EPOCHS

	print("TRAINING FEED FORWARD NN... MAY TAKE A WHILE")
	t3 = time()

	# For each epoch
	for e in range(0, EPOCHS):
		print("Training Epoch {}...".format(e))
		all_y_pred = []
		train_batches = zip(train_batches_X, train_batches_Y)

		# For each mini batch
		for tr_batch_X, tr_batch_Y in train_batches:

			# Forward pass
			optimizer.zero_grad()
			y_pred = model(tr_batch_X)
			all_y_pred.append(y_pred)
			labels = torch.max(tr_batch_Y, 1)[1]

			# Loss
			loss = criterion(y_pred, labels)

			# Backward pass
			loss.backward()
			optimizer.step()

		# Evaluate, save epoch level training accuracies & f1 score
		all_y_pred = torch.cat(all_y_pred, dim=0)
		acc, f1sc, acc_array, f1_array = evaluate(all_y_pred, train_Y)
		epoch_accs[e] = acc
		epoch_f1s[e] = f1sc

		epoch_accs_B[e] = acc_array[0]
		epoch_accs_I[e] = acc_array[1]
		epoch_accs_O[e] = acc_array[2]

		epoch_f1s_B[e] = f1_array[0]
		epoch_f1s_I[e] = f1_array[1]
		epoch_f1s_O[e] = f1_array[2]

	t4 = time()
	print("Training FFNN Complete. Training Time: {} Minutes.\n".format((t4-t3) / 60 ))

	print("------------Training Metrics-----------")
	for e in range(EPOCHS):
		print("Epoch {} : total acc: {} total f1: {}".format(e, epoch_accs[e], epoch_f1s[e]))
		print("Epoch {} : B level acc {} B level f1: {}".format(e, epoch_accs_B[e], epoch_f1s_B[e]))
		print("Epoch {} : I level acc {} I level f1: {}".format(e, epoch_accs_I[e], epoch_f1s_I[e]))
		print("Epoch {} : O level acc {} O level f1: {}".format(e, epoch_accs_O[e], epoch_f1s_O[e]))
	print("\nFinal : total acc: {} total f1: {}".format(epoch_accs[EPOCHS-1], epoch_f1s[EPOCHS-1]))
	print("Final : B level acc {} B level f1: {}".format(epoch_accs_B[EPOCHS-1], epoch_f1s_B[EPOCHS-1]))
	print("Final : I level acc {} I level f1: {}".format(epoch_accs_I[EPOCHS-1], epoch_f1s_I[EPOCHS-1]))
	print("Final : O level acc {} O level f1: {}".format(epoch_accs_O[EPOCHS-1], epoch_f1s_O[EPOCHS-1]))

	# Test
	y_pred_test = model(test_X)
	test_acc, test_f1sc, test_acc_array, test_f1_array = evaluate(y_pred_test, test_Y)

	print("\n------------Testing Metrics-----------".format(epoch_accs))
	print("Test acc total: {} test f1 total: {}".format(test_acc, test_f1sc))
	print("Test acc B-level: {} test f1 B-level {}".format(test_acc_array[0], test_f1_array[0]))
	print("Test acc I-level: {} test f1 I-level {}".format(test_acc_array[1], test_f1_array[1]))
	print("Test acc O-level: {} test f1 O-level {}".format(test_acc_array[2], test_f1_array[2]))

	print("\n------------Additional-----------")
	print("Num Training Instances: {}".format(TRAIN_INSTANCES))

if __name__ == '__main__':
	main()