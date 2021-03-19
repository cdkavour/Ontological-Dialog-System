########
# DATA #
########

data 
	↳ unprocessed
		↳ hw3_train.txt - the training data used to create the CRF slot tagger used in preprocesseding

		↳ *.tsv - individual group full dialogues from HW1 in standardized format, ready to be tagged with slot

	↳ data4_silver_annotations
		↳ *.tsv - the resulting files from running the slot tagger on HW1 data.  Contains slot tags like "pizza_type" but not tags for referring expressions or referents

	↳ data4_annotated_for_ref
		↳ train
			*_annotated.tsv - hand-annotations from referring expressions and referents for all groups' data except our own.  Derived from the files in data/data4_silver_annotations

		↳ kavouras_ng.tsv - hand-annotations from referring expressions and referents for our own data, to be used only in evaluation

###########
# SCRIPTS #
###########

# helper scripts

eval.py - contains functions for accuracy and class_accuracy;  called by baseline.py and crf.py

# preprocessing scripts

calc_ref_distance.py - used to determine what a reasonable turn history to look at is.  Searches through the hand-annotated data in data/data4_annotated_for_ref/train for referring expressions and their referents, figures out the coverage, and plots the distribution.

	invocation:  python3 calc_ref_distance.py > distance_summary
	files produced: distance_summary, distances.png

label_data_4.py - a near-copy of the script used to label slots in HW4

	invocation:  python3  label_data_4.py --noise $NOISE_COEFFICIENT
	files produced:  data/data4_silver_annotations/*

# models

baseline.py - the baselines for parts I and II, with results printed to a single file.  Run with num_turns = 6 and 10. Prints evaluation measures to text file.

	invocation:  python3 baseline.py --num_turns $NUMBER_OF_TURNS_IN_HISTORY > baseline_${NUMBER_OF_TURNS_IN_HISTORY}
	files produced:  baseline_${NUMBER_OF_TURNS_IN_HISTORY}

crf.py - train and run a CRF for either refexp tagging or referent detection.  Run with num_turns = 6 and 10.  Prints evaluation measures to text file.

	invocation:  python3 crf.py --num_turns $NUMBER_OF_TURNS_IN_HISTORY > crf_${NUMBER_OF_TURNS_IN_HISTORY}
	files produced:  crf_${NUMBER_OF_TURNS_IN_HISTORY}

##################
# COMMAND SAMPLE #
##################

NOISE_COEFFICIENT=0.05
python3 calc_ref_distance.py > distance_summary
python3  label_data_4.py --noise $NOISE_COEFFICIENT

NUMBER_OF_TURNS_IN_HISTORY=6
python3 baseline.py --num_turns $NUMBER_OF_TURNS_IN_HISTORY > baseline_${NUMBER_OF_TURNS_IN_HISTORY}
python3 crf.py --num_turns $NUMBER_OF_TURNS_IN_HISTORY > crf_${NUMBER_OF_TURNS_IN_HISTORY}

NUMBER_OF_TURNS_IN_HISTORY=10
python3 baseline.py --num_turns $NUMBER_OF_TURNS_IN_HISTORY > baseline_${NUMBER_OF_TURNS_IN_HISTORY}
python3 crf.py --num_turns $NUMBER_OF_TURNS_IN_HISTORY > crf_${NUMBER_OF_TURNS_IN_HISTORY}