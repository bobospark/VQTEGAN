# Easy data augmentation techniques for text classification
# Jason Wei, Chengyu Huang, Yifang Wei, Fei Xing, Kai Zou

import random
from random import shuffle
random.seed(1)

#stop words list
stop_words = ['i', 'me', 'my', 'myself', 'we', 'our', 
			'ours', 'ourselves', 'you', 'your', 'yours', 
			'yourself', 'yourselves', 'he', 'him', 'his', 
			'himself', 'she', 'her', 'hers', 'herself', 
			'it', 'its', 'itself', 'they', 'them', 'their', 
			'theirs', 'themselves', 'what', 'which', 'who', 
			'whom', 'this', 'that', 'these', 'those', 'am', 
			'is', 'are', 'was', 'were', 'be', 'been', 'being', 
			'have', 'has', 'had', 'having', 'do', 'does', 'did',
			'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or',
			'because', 'as', 'until', 'while', 'of', 'at', 
			'by', 'for', 'with', 'about', 'against', 'between',
			'into', 'through', 'during', 'before', 'after', 
			'above', 'below', 'to', 'from', 'up', 'down', 'in',
			'out', 'on', 'off', 'over', 'under', 'again', 
			'further', 'then', 'once', 'here', 'there', 'when', 
			'where', 'why', 'how', 'all', 'any', 'both', 'each', 
			'few', 'more', 'most', 'other', 'some', 'such', 'no', 
			'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 
			'very', 's', 't', 'can', 'will', 'just', 'don', 
			'should', 'now', '']

#cleaning up text
import re
def get_only_chars(line):

    clean_line = ""

    line = line.replace("’", "")
    line = line.replace("'", "")
    line = line.replace("-", " ") #replace hyphens with spaces
    line = line.replace("\t", " ")
    line = line.replace("\n", " ")
    line = line.lower()

    for char in line:
        if char in 'qwertyuiopasdfghjklzxcvbnm ':
            clean_line += char
        else:
            clean_line += ' '

    clean_line = re.sub(' +',' ',clean_line) #delete extra spaces
    if clean_line[0] == ' ':
        clean_line = clean_line[1:]
    return clean_line

########################################################################
# Synonym replacement
# Replace n words in the sentence with synonyms from wordnet
########################################################################

#for the first time you use wordnet
#import nltk
#nltk.download('wordnet')
from nltk.corpus import wordnet 

def synonym_replacement(words, n):
	new_words = words.copy()
	random_word_list = list(set([word for word in words if word not in stop_words]))
	random.shuffle(random_word_list)
	num_replaced = 0
	for random_word in random_word_list:
		synonyms = get_synonyms(random_word)
		if len(synonyms) >= 1:
			synonym = random.choice(list(synonyms))
			new_words = [synonym if word == random_word else word for word in new_words]
			#print("replaced", random_word, "with", synonym)
			num_replaced += 1
		if num_replaced >= n: #only replace up to n words
			break

	#this is stupid but we need it, trust me
	sentence = ' '.join(new_words)
	new_words = sentence.split(' ')

	return new_words

def get_synonyms(word):
	synonyms = set()
	for syn in wordnet.synsets(word): 
		for l in syn.lemmas(): 
			synonym = l.name().replace("_", " ").replace("-", " ").lower()
			synonym = "".join([char for char in synonym if char in ' qwertyuiopasdfghjklzxcvbnm'])
			synonyms.add(synonym) 
	if word in synonyms:
		synonyms.remove(word)
	return list(synonyms)

########################################################################
# Random deletion
# Randomly delete words from the sentence with probability p
########################################################################

def random_deletion(words, p):

	#obviously, if there's only one word, don't delete it
	if len(words) == 1:
		return words

	#randomly delete words with probability p
	new_words = []
	for word in words:
		r = random.uniform(0, 1)
		if r > p:
			new_words.append(word)

	#if you end up deleting all words, just return a random word
	if len(new_words) == 0:
		rand_int = random.randint(0, len(words)-1)
		return [words[rand_int]]

	return new_words

########################################################################
# Random swap
# Randomly swap two words in the sentence n times
########################################################################

def random_swap(words, n):
	new_words = words.copy()
	for _ in range(n):
		new_words = swap_word(new_words)
	return new_words

def swap_word(new_words):
	random_idx_1 = random.randint(0, len(new_words)-1)
	random_idx_2 = random_idx_1
	counter = 0
	while random_idx_2 == random_idx_1:
		random_idx_2 = random.randint(0, len(new_words)-1)
		counter += 1
		if counter > 3:
			return new_words
	new_words[random_idx_1], new_words[random_idx_2] = new_words[random_idx_2], new_words[random_idx_1] 
	return new_words

########################################################################
# Random addition
# Randomly add n words into the sentence
########################################################################

def random_addition(words, n):
	new_words = words.copy()
	for _ in range(n):
		add_word(new_words)
	return new_words

def add_word(new_words):
	synonyms = []
	counter = 0
	while len(synonyms) < 1:
		random_word = new_words[random.randint(0, len(new_words)-1)]
		synonyms = get_synonyms(random_word)
		counter += 1
		if counter >= 10:
			return
	random_synonym = synonyms[0]
	random_idx = random.randint(0, len(new_words)-1)
	new_words.insert(random_idx, random_synonym)

########################################################################
# main data augmentation function
########################################################################

def eda_4(sentences, alpha_sr=0.3, alpha_ri=0.2, alpha_rs=0.1, p_rd=0.15, num_aug=0):

    augmented_sentences_output, augmented_labels_output, augmented_idx_output = [], [], []

    features = [i for i in sentences.keys()]

    if len(features) == 3: 
		
        for i, sentence in enumerate(sentences[features[0]]):  # features[0] = 'sentence'
            sentence = get_only_chars(sentence)
            words = sentence.split(' ')
            words = [word for word in words if word != '']
            num_words = len(words)
            

            num_new_per_technique = int(num_aug/4)+1
            n_sr = max(1, int(alpha_sr*num_words))
            n_ri = max(1, int(alpha_ri*num_words))
            n_rs = max(1, int(alpha_rs*num_words))

            augmented_sentences = []
            #sr
            for _ in range(num_new_per_technique):
                a_words = synonym_replacement(words, n_sr)
                augmented_sentences.append(' '.join(a_words))

            #ri
            for _ in range(num_new_per_technique):
                a_words = random_addition(words, n_ri)
                augmented_sentences.append(' '.join(a_words))

            #rs
            for _ in range(num_new_per_technique):
                a_words = random_swap(words, n_rs)
                augmented_sentences.append(' '.join(a_words))

            #rd
            for _ in range(num_new_per_technique):
                a_words = random_deletion(words, p_rd)
                augmented_sentences.append(' '.join(a_words))

            augmented_sentences = [get_only_chars(sentence) for sentence in augmented_sentences]
            shuffle(augmented_sentences)

            #trim so that we have the desired number of augmented sentences
            if num_aug >= 1:
                augmented_sentences = augmented_sentences[:num_aug]
            else:
                keep_prob = num_aug / len(augmented_sentences)
                augmented_sentences = [s for s in augmented_sentences if random.uniform(0, 1) < keep_prob]

            #append the original sentence
            augmented_sentences.append(sentence)
            
            #append the original sentence index
            for sen in augmented_sentences:
                augmented_sentences_output.append(sen)
            # augmented_sentences_output.append(augmented_sentences)
            
            #append the original index
            augmented_idx = [sentences['idx'][i] for _ in range(len(augmented_sentences))]
            for idx in augmented_idx:
                augmented_idx_output.append(idx)
            # augmented_idx_output.append(augmented_idx)
            
            #append the original label
            augmented_labels = [sentences['label'][i] for _ in range(len(augmented_sentences))]
            for label in augmented_labels:
                augmented_labels_output.append(label)
            # augmented_labels_output.append(augmented_labels)
        
        output = {features[0]: augmented_sentences_output, features[1]: augmented_labels_output, 'idx': augmented_idx_output}

    if len(features) == 4: 
        augmented_sentences_output = [[],[]]
		
        for i, sentence in enumerate(zip(sentences[features[0]], sentences[features[1]])):

            for sen_num in range(2):
                sentence_ = get_only_chars(sentence[sen_num])
                words = sentence_.split(' ')
                words = [word for word in words if word != '']
                num_words = len(words)
                
                num_new_per_technique = int(num_aug/4)+1
                n_sr = max(1, int(alpha_sr*num_words))
                n_ri = max(1, int(alpha_ri*num_words))
                n_rs = max(1, int(alpha_rs*num_words))

                augmented_sentences = []
                #sr
                for _ in range(num_new_per_technique):
                    a_words = synonym_replacement(words, n_sr)
                    augmented_sentences.append(' '.join(a_words))

                #ri
                for _ in range(num_new_per_technique):
                    a_words = random_addition(words, n_ri)
                    augmented_sentences.append(' '.join(a_words))

                #rs
                for _ in range(num_new_per_technique):
                    a_words = random_swap(words, n_rs)
                    augmented_sentences.append(' '.join(a_words))

                #rd
                for _ in range(num_new_per_technique):
                    a_words = random_deletion(words, p_rd)
                    augmented_sentences.append(' '.join(a_words))

                augmented_sentences = [get_only_chars(augmented_sentence) for augmented_sentence in augmented_sentences]
                shuffle(augmented_sentences)

                #trim so that we have the desired number of augmented sentences
                if num_aug >= 1:
                    augmented_sentences = augmented_sentences[:num_aug]
                else:
                    keep_prob = num_aug / len(augmented_sentences)
                    augmented_sentences = [s for s in augmented_sentences if random.uniform(0, 1) < keep_prob]

                #append the original sentence
                augmented_sentences.append(sentence_)
                
                #append the original sentence index
                for sen in augmented_sentences:
                    augmented_sentences_output[sen_num].append(sen)
                # augmented_sentences_output.append(augmented_sentences)
                
            #append the original index
            augmented_idx = [sentences['idx'][i] for _ in range(len(augmented_sentences))]
            for idx in augmented_idx:
                augmented_idx_output.append(idx)
            # augmented_idx_output.append(augmented_idx)
            
            #append the original label
            augmented_labels = [sentences['label'][i] for _ in range(len(augmented_sentences))]
            for label in augmented_labels:
                augmented_labels_output.append(label)
            # augmented_labels_output.append(augmented_labels)
        
        output = {features[0]: augmented_sentences_output[0], features[1] : augmented_sentences_output[1],'label': augmented_labels_output, 'idx': augmented_idx_output}

    return output

def SR(sentence, alpha_sr, n_aug=9):

	sentence = get_only_chars(sentence)
	words = sentence.split(' ')
	num_words = len(words)

	augmented_sentences = []
	n_sr = max(1, int(alpha_sr*num_words))

	for _ in range(n_aug):
		a_words = synonym_replacement(words, n_sr)
		augmented_sentences.append(' '.join(a_words))

	augmented_sentences = [get_only_chars(sentence) for sentence in augmented_sentences]
	shuffle(augmented_sentences)

	augmented_sentences.append(sentence)

	return augmented_sentences

def RI(sentence, alpha_ri, n_aug=9):

	sentence = get_only_chars(sentence)
	words = sentence.split(' ')
	num_words = len(words)

	augmented_sentences = []
	n_ri = max(1, int(alpha_ri*num_words))

	for _ in range(n_aug):
		a_words = random_addition(words, n_ri)
		augmented_sentences.append(' '.join(a_words))

	augmented_sentences = [get_only_chars(sentence) for sentence in augmented_sentences]
	shuffle(augmented_sentences)

	augmented_sentences.append(sentence)

	return augmented_sentences

def RS(sentence, alpha_rs, n_aug=9):

	sentence = get_only_chars(sentence)
	words = sentence.split(' ')
	num_words = len(words)

	augmented_sentences = []
	n_rs = max(1, int(alpha_rs*num_words))

	for _ in range(n_aug):
		a_words = random_swap(words, n_rs)
		augmented_sentences.append(' '.join(a_words))

	augmented_sentences = [get_only_chars(sentence) for sentence in augmented_sentences]
	shuffle(augmented_sentences)

	augmented_sentences.append(sentence)

	return augmented_sentences

def RD(sentence, alpha_rd, n_aug=9):

	sentence = get_only_chars(sentence)
	words = sentence.split(' ')
	words = [word for word in words if word != '']
	num_words = len(words)

	augmented_sentences = []

	for _ in range(n_aug):
		a_words = random_deletion(words, alpha_rd)
		augmented_sentences.append(' '.join(a_words))

	augmented_sentences = [get_only_chars(sentence) for sentence in augmented_sentences]
	shuffle(augmented_sentences)

	augmented_sentences.append(sentence)

	return augmented_sentences




















########################################################################
# Testing
########################################################################

if __name__ == '__main__':

	line = 'Hi. My name is Jason. I’m a third-year computer science major at Dartmouth College, interested in deep learning and computer vision. My advisor is Saeed Hassanpour. I’m currently working on deep learning for lung cancer classification.'



########################################################################
# Sliding window
# Slide a window of size w over the sentence with stride s
# Returns a list of lists of words
########################################################################

# def sliding_window_sentences(words, w, s):
# 	windows = []
# 	for i in range(0, len(words)-w+1, s):
# 		window = words[i:i+w]
# 		windows.append(window)
# 	return windows