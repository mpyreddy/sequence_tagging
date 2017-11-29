import argparse
import numpy as np

def load_sentence(line_array):
    words = []
    tags = []
    for line in line_array:
        word, tag = line.split(' ')
        words.append(word)
        tags.append(tag)
    return words, tags

def mapping(kp_filename, ner_filename):
    f_kp = open(kp_filename)
    data_kp = f_kp.read().strip().split('\n')
    f_ner = open(ner_filename)
    data_ner = f_ner.read().strip().split('\n')

    line_num_ner = 0
    line_num_kp = 0
    while line_num_kp < len(data_kp):
        if line_num_kp % 1000 == 0:
            print "processed {} lines".format(line_num_kp)
        while data_kp[line_num_kp] == '':
            line_num_kp += 1
        while data_ner[line_num_ner] == '':
            line_num_ner += 1
        print data_kp[line_num_kp]
        word_kp, tag_kp = data_kp[line_num_kp].split(' ')
        word_ner, tag_ner = data_ner[line_num_ner].split(' ')
        if word_kp == word_ner:
            line_num_kp += 1
            line_num_ner += 1
            pass
        else:
            import pdb;pdb.set_trace()


def evaluate(kp_filename, ner_filename):
    kp_data = open(kp_filename).read().strip().split('\n\n')
    ner_data = open(ner_filename).read().strip().split('\n\n')

    accs = []
    correct_preds, total_preds, total_correct = 0., 0., 0.
    for lab, lab_pred in zip(kp_data, ner_data):
        lab = [w.split(' ')[1] for w in lab.split('\n')]
        lab_pred = [w.split(' ')[1] for w in lab_pred.split('\n')]

        for (a, b) in zip(lab, lab_pred):
            if a != "O":
                total_correct += 1

            if b != "O":
                total_preds += 1

            if a != "O" and b != "O":
                correct_preds += 1

            if a == "O" and b == "O":
                accs.append(1)

            elif "KP" in a and b != "O":
                accs.append(1)

            else:
                accs.append(0)

    p = correct_preds / total_preds if correct_preds > 0 else 0
    r = correct_preds / total_correct if correct_preds > 0 else 0
    f1 = 2 * p * r / (p + r) if correct_preds > 0 else 0
    acc = np.mean(accs)

    print "Accuracy = {}, F1Score = {}, Precision = {}, Recall = {}".format(acc, f1, p, r)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("kp_file")
    parser.add_argument("ner_file")
    args = parser.parse_args()
    #mapping(args.kp_file, args.ner_file)
    evaluate(args.kp_file, args.ner_file)