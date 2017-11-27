import argparse
import json
import random
import re
from collections import defaultdict
from textblob import TextBlob
import nltk


def getSentenceLevelData(articles_filename, dataset, result_filename):
    def spans(txt, para_offset):
        tokens = nltk.word_tokenize(txt)
        result = []
        offset = 0
        for token in tokens:
            #token_orig = re.sub('``', '"', token)
            #token_orig = re.sub("''", '"', token_orig)
            new_offset = txt.find(token, offset)
            result.append((token, para_offset + new_offset, para_offset + new_offset + len(token)))
            if new_offset == -1:
                continue
            offset = new_offset + len(token)
        return result

    result_words = []
    result_tags = []
    counter = 0

    articles = set(open(articles_filename).read().splitlines())

    f_sent = open(result_filename, "w")
    line_num = 0
    for i in range(len(dataset)):
        if dataset[i]['title'] not in articles:
            continue
        for j in range(len(dataset[i]['paragraphs'])):
            context = re.sub(r'[^\x00-\x7F]',' ', dataset[i]['paragraphs'][j]['context'])
            context = re.sub(r'-', ' ', context)
            #context = re.sub("\n", ". ", context)
            sentences = TextBlob(context).sentences
            sentences_end_index = []
            para_words = []
            para_info = []
            c_dist = 0
            for s in range(len(sentences)):
                words = spans(str(sentences[s]), sentences[s].start)
                para_words.append([word[0] for word in words])
                para_info.append(words)
                sent = sentences[s]
                c_dist += sent.end
                sentences_end_index.append(c_dist)

            try:
                assert len(sentences) == len(sentences_end_index)
            except Exception as e:
                import pdb;
                pdb.set_trace()

            para_tags = []
            for sent_words in para_words:
                para_tags.append(["O"]*len(sent_words))

            qas = dataset[i]['paragraphs'][j]['qas']

            num_sentences = len(sentences_end_index)
            k = 0
            while k < num_sentences:
                for qa in qas:
                    for ans in qa['answers']:
                        start = int(ans['answer_start'])
                        answer_phrase = re.sub(r'[^\x00-\x7F]+',' ', ans['text'].lower())
                        answer_phrase = re.sub(r'-', ' ', answer_phrase)

                        answer_words = nltk.word_tokenize(answer_phrase)

                        num_words_sent = len(para_info[k])
                        w = 0
                        while w < num_words_sent:
                            if para_info[k][w][1] == start:
                                while w + len(answer_words) > len(para_info[k]):
                                    try:
                                        para_info[k] += para_info[k+1]
                                    except:
                                        import pdb;pdb.set_trace()
                                    del para_info[k+1]
                                    para_words[k] += para_words[k+1]
                                    del para_words[k+1]
                                    para_tags[k] += para_tags[k+1]
                                    del para_tags[k+1]
                                    num_words_sent = len(para_info[k])
                                    num_sentences -= 1
                                for aw in range(w, w+len(answer_words)):
                                    try:
                                        if aw == w:
                                            para_tags[k][aw] = "B-KP"
                                        else:
                                            para_tags[k][aw] = "I-KP"
                                    except Exception as e:
                                        print para_words[k], answer_phrase
                                        counter += 1
                                        import pdb;pdb.set_trace()
                            w += 1
                        # if answer_phrase in sentences[k].lower():
                        #     if ((k > 0 and sentences_end_index[k - 1] <= start and start < sentences_end_index[k]) \
                        #                 or (k == 0 and start <= sentences_end_index[k])):
                        #         start_index = 0
                        #         found_start_word = False
                        #         for w in range(len(para_words[k])):
                        #             if not found_start_word:
                        #                 if para_words[k][w].lower() == answer_words[0]:
                        #                     found_start_word = True
                        #                     start_index = w
                        #             if found_start_word:
                        #                 for aw in range(len(answer_words)):
                        #                     if ((w+aw) >= len(para_words[k])) or para_words[k][w + aw].lower() != answer_words[aw]:
                        #                         found_start_word = False
                        #                         break
                        #                 if found_start_word:
                        #                     break
                        #         if found_start_word:
                        #             for aw in range(start_index, start_index + len(answer_words)):
                        #                 para_tags[k][aw] = True
                        #         else:
                        #             print para_words[k], answer_phrase
                k += 1
            result_words += para_words
            result_tags += para_tags
    print counter

    f = open(result_filename, "w")
    for sent in range(len(result_words)):
        for word in range(len(result_words[sent])):
            f.write(result_words[sent][word] + " " + result_tags[sent][word] + "\n")
        f.write("\n")



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("config_file")
    args = parser.parse_args()

    c = json.load(open(args.config_file))
    squad_train_file = c["squad_train_file"]
    squad_dev_file = c["squad_dev_file"]
    articles_train_file = c["articles_train_file"]
    articles_dev_file = c["articles_dev_file"]
    articles_test_file = c["articles_test_file"]
    train_filename = c["train_file"]
    dev_filename = c["dev_file"]
    test_filename = c["test_file"]


    random.seed(42)
    train_dataset = json.load(open(squad_train_file))
    dev_dataset = json.load(open(squad_dev_file))

    total_articles = train_dataset['data'] + dev_dataset['data']


    getSentenceLevelData(articles_train_file, total_articles, train_filename)
    getSentenceLevelData(articles_dev_file, total_articles, dev_filename)
    getSentenceLevelData(articles_test_file, total_articles, test_filename)