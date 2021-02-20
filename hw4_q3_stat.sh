#!/bin/sh

python3 slot_labeling.py -n 0
python3 IntentClassifyStatBased.py DATA5/DATA5.txt ngrams+slots+hand_picked
