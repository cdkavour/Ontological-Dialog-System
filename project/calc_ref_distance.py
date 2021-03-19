from bs4 import BeautifulSoup
import glob
import math
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

''' look at the distribution of distances  betweeen refexps and referents
sara ng
last modified 19 march, 2021
'''


def main():
	# load in all of the files
	data_path = 'data/data4_annotated_for_ref/train/*'
	files = glob.glob(data_path)
	distances = []
	for file in files:
		with open(file,'r') as f:
			data = pd.read_csv(f,sep='\t')
		grouped = data.groupby(['Conversation'])
		titles = grouped.groups.keys()
		group_dict = {title:grouped.get_group(title) for title in titles}

		# for each conversation in that file, pull the distances
		for title,dataframe in group_dict.items():
			transcripts = list(dataframe.Transcript.values)
			refs = []
			refs_indices = []
			for idx,transcript in enumerate(transcripts):
				soup = BeautifulSoup(transcript,'html.parser')
				transcript_refs = [i['id'] for i in soup.find_all('ref')]
				refs += transcript_refs
				refs_indices += [idx]*len(transcript_refs)
				refexps = [i['id'] for i in soup.find_all('refexp')]
				for refexp in refexps:
					try:
						distance = idx-refs_indices[refs.index(refexp)]
					except ValueError:
						distance = None
					distances.append(distance)
	print('{} referring expressions found'.format(len(distances)))
	print('{} refexps have no referent'.format(distances.count(None)))
	with_referent = [d for d in distances if d != None]

	mu = np.mean(with_referent)
	sigma = np.std(with_referent)
	print('mean = {:.3f}\nstd devation = {:.3f}'.format(mu,sigma))
	
	# plot distribution
	num_bins = 25
	n, bins, patches = plt.hist(with_referent, num_bins, facecolor='blue', alpha=0.5)
	plt.xlabel('Distance from refexp to referent in turns')
	plt.ylabel('Probability')
	plt.title(r'Referential distance: $\mu={:.3f}$, $\sigma={:.3f}$'.format(mu,sigma))
	plt.subplots_adjust(left=0.15)
	plt.savefig('results/distances.png')

	# figure out how many turns make sense
	for_free = distances.count(None)
	median = np.median(with_referent)
	one_z = math.ceil(mu + sigma)
	two_z = math.ceil(mu + 2*sigma)
	mostly_covered = [a for a in with_referent if a <= one_z]
	covered = [a for a in with_referent if a <= two_z]
	print('{:.2f}% of data covered in {} turns'.format((len(mostly_covered)+for_free)/len(distances)*100,one_z))
	print('{:.2f}% of data covered in {} turns'.format((len(covered)+for_free)/len(distances)*100,two_z))


if __name__ == "__main__":
	main()
