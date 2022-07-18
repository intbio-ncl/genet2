
import string
import nltk
import re

from fuzzywuzzy import fuzz,process

class LanguageUtil:
    def __init__(self,blacklist_words=[],whitelist_words=[]):
        self.stop_words = set(nltk.corpus.stopwords.words('english'))
        self.prune_pos_tags = ["DT","PRP$","WRB","MD","EX","$","RBS",
                               "RBR","JJS","WP","SYM","RP","WDT"]
        self.blacklist_words = blacklist_words
        self.whitelist_words = whitelist_words

    def fuzzy_string_match(self,search_term,expected_terms,confidence_threshold=70):
        if len(expected_terms) == 0:
            return False

        highest_confidence_score = process.extractOne(search_term, expected_terms,
                                                      scorer=fuzz.token_sort_ratio)
        if highest_confidence_score[1] >= confidence_threshold:
            return True
        return False

    # ------------------------ Sentences Level ------------------------
    def mine_sentences(self,sentences):
        mined_words = []
        sentences = self.tokenize_sentences(sentences)
        for sentence in sentences:
            mined_words = mined_words + self.mine_sentence(sentence)
        return list(set(mined_words))

    def tokenize_sentences(self,sentences):
        sentences = nltk.sent_tokenize(sentences)
        return sentences

    def pos_tag_sentences(self,sentences):
        sentences = [nltk.pos_tag(sent) for sent in sentences]
        return sentences

    # ------------------------ Sentence Level ------------------------
    def mine_sentence(self,sentence):
        words = self.tokenize_sentence(sentence)
        pos_tagged_words = self.pos_tag_sentence(words)
        mined_words = []
        for word,tag in pos_tagged_words:
            mined_words = mined_words + self.mine_word(word,tag)
        return list(set(mined_words))

    def tokenize_sentence(self,sentence):
        words = nltk.word_tokenize(sentence)
        return words

    def pos_tag_sentence(self,sentence):
        sentences = nltk.pos_tag(sentence)
        return sentences

    # ------------------------ Word Level ------------------------
    def mine_word(self,word,pos_tag=None):
        words = []
        tokens = self.tokenize_word(word)
        for token in tokens:
            if self.is_valid_token(token,pos_tag):
                words.append(token.lower())
        return words
        
    def tokenize_word(self,word):
        return re.split("[" + string.punctuation + "]+", word)

    # ------------------------ Token Level ------------------------
    def is_valid_token(self,token,pos_tag=None):
        blacklist_confidence = 90
        if len(token) <= 2:
            return False
        if not token.isalpha():
            return False
        if token in self.stop_words:
            return False
        if token in self.prune_pos_tags:
            return False
        highest_confidence_score = process.extractOne(token, self.blacklist_words)
        if highest_confidence_score[1] >= blacklist_confidence:
            return False
        return True


    def get_name(self,subject):
        split_subject = self.split(subject)
        if len(split_subject[-1]) == 1 and split_subject[-1].isdigit():
            return split_subject[-2]
        else:
            return split_subject[-1]
    
    def split(self,uri):
        return re.split('#|\/|:', uri)


    