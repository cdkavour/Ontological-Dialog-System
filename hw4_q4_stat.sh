#!/bin/sh

python3 slot_labeling.py -n 0.5
python3 IntentClassifyStatBased.py DATA6/DATA6.txt ngrams+slots+hand_picked
