import sys
from NLURuleBased import NLURuleBased
import ipdb

def get_data(data_file, annotated_data_file):
    labels = []
    instances = []

    with open(data_file) as df:
        data_lines = df.readlines()[1:]

    with open(annotated_data_file) as adf:
        annotated_data_lines = adf.readlines()[1:] 

    for i in range(len(data_lines)):
        data_line = data_lines[i]
        annotated_data_line = annotated_data_lines[i]

        _, _, instance = data_line.split('\t', 2)
        instance = instance.rstrip()

        label = annotated_data_line.split()[0]

        labels.append(label)
        instances.append(instance)

    return labels, instances

def annotate_data0():
    data0file = "shared-filtered"
    with open(data0file) as d0f:
        d0lines = d0f.readlines()
    for line in d0lines:
        annotation = NLU.parse(line)
        print(annotation)
        NLU.printSemanticFrame()
        NLU.clear_slots()

def annotate_data(NLU):
    annotations = []
    pred_labels = []

    data_file_5_1 = "DATA5/part1.tsv"
    data_file_5_1_annotated = "DATA5/part1_annotated.tsv"
    data_file_5_2 = "DATA5/part2.tsv"
    data_file_5_2_annotated = "DATA5/part2_annotated.tsv"
    data_file_6_1 = "DATA6/part1.tsv"
    data_file_6_1_annotated = "DATA6/part1_annotated.tsv"
    data_file_6_2 = "DATA6/part2.tsv"
    data_file_6_2_annotated = "DATA6/part2_annotated.tsv"

    data_5_1_labels, data_5_1_instances = get_data(data_file_5_1, data_file_5_1_annotated)
    data_5_2_labels, data_5_2_instances = get_data(data_file_5_2, data_file_5_1_annotated)
    data_6_1_labels, data_6_1_instances = get_data(data_file_6_1, data_file_5_1_annotated)
    data_6_2_labels, data_6_2_instances = get_data(data_file_6_2, data_file_5_1_annotated)

    #true_labels = data_5_1_labels + data_5_2_labels + data_6_1_labels + data_6_2_labels
    #instances = data_5_1_instances + data_5_2_instances + data_6_1_instances + data_6_2_instances

    true_labels = data_5_1_labels + data_5_2_labels
    instances = data_5_1_instances + data_5_2_instances

    #true_labels = data_6_1_labels + data_6_2_labels
    #instances = data_6_1_instances + data_6_2_instances

    pred_labels = []
    annotations = []
    for instance in instances:
        annotation = NLU.parse(instance)
        annotations.append(annotation)
        pred_label = NLU.SemanticFrame.Intent.name
        pred_labels.append(pred_label)

    return annotations, pred_labels, true_labels, instances

def accuracy(pred_labels, true_labels):
    correct =  sum(pred_labels[i] == true_labels[i] for i in range(len(pred_labels)))
    total = len(pred_labels)

    return float(correct) / float(total)

def main():
    NLU = NLURuleBased()

    annotations, pred_labels, true_labels, instances = annotate_data(NLU)
    acc = accuracy(pred_labels, true_labels)

    print("accuracy on data 5: ", acc)
    #ipdb.set_trace()

    print("Rule based NLU - enter query:")

    while(True):
        inputStr = input("> ")
        if (inputStr == "Quit"):
            break
        annotation = NLU.parse(inputStr)
        #ipdb.set_trace()
        NLU.printSemanticFrame()
        print(annotation)
        NLU.clear_slots()

if __name__ == '__main__':
    main()