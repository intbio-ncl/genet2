import spacy
from fuzzywuzzy import fuzz,process

'''
Note this doesn't really work.
It just returns the subjects of potential sentences.
'''
class LanguageAnalyser:
    def __init__(self,blacklist_words = [], whitelist_words = []):
        self.nlp = spacy.load('en_core_web_sm')

    def fuzzy_string_match(self,search_term,expected_terms,confidence_threshold=70):
        if len(expected_terms) == 0:
            return False

        highest_confidence_score = process.extractOne(search_term, expected_terms,
                                                      scorer=fuzz.token_sort_ratio)
        if highest_confidence_score[1] >= confidence_threshold:
            return True
        return False

    def get_subjects(self,sentences):
        subjects = []
        doc=self.nlp(sentences)
        for sentence in list(doc.sents):
            subjects += [str(tok) for tok in sentence if (tok.dep_ == "nsubj") ]
        return list(set(subjects))

    def get_subject(self,sentence):
        doc=self.nlp(sentence)
        sub_toks = [tok for tok in doc if (tok.dep_ == "nsubj") ]
        return sub_toks