#!/bin/sh

python3 slot_labeling.py
python3 IntentClassifyStatBased.py dev_set ngrams
