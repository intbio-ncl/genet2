import rdflib

from graph.knowledge.data_miner.language.utility import LanguageUtil
from utility.sbol_identifiers import identifiers

'''
Sentence Segmenation -> Tokenization -> Part of speech tagging -> Entity Detection     -> Relation Detection
            Raw Text -> Sentences    -> Tokenized sentences    -> Pos-tagged Sentences -> Chunked Sentences -> Relations
            String   -> List<String> -> List<List<String>>     -> List<List<Tuple>>    -> List<Tree>        -> List<Tuples> 
'''

'''
8 Parts of Speech 
1. NOUN - the name of a person, place, thing, or idea.
2. PRONOUN - used in place of a noun.
3. VERB - Expresses action or being.
4. ADJECTIVE - modifies or describes a noun or pronoun.
5. ADVERB - modifies or describes a verb, an adjective, or another adverb.
6. PREPOSITION - placed before a noun or pronoun to form a phrase modifying another word in the sentence.
7. CONJUNCTION - joins words, phrases, or clauses.
8. INTERJECTION - used to express emotion.
'''
'''
https://cheatography.com/murenei/cheat-sheets/natural-language-processing-with-python-and-nltk/
https://cheatography.com/deacondesperado/cheat-sheets/nltk-part-of-speech-tags/
'''

manual_blacklist = ["bba"]
descriptor_predicates = [identifiers.predicates.title,
                        identifiers.predicates.description,
                        identifiers.predicates.mutable_description,
                        identifiers.predicates.mutable_notes,
                        identifiers.predicates.mutable_provenance]


class LanguageAnalyser:
    def __init__(self,blacklist_words = [], whitelist_words = []):
        blacklist_words = []#self._produce_blacklist_words()
        whitelist_words = []
        self._util = LanguageUtil(blacklist_words, whitelist_words)
    
    def get_aliases(self,texts=[],triples=[]):
        aliases = []
        for text in texts:
            aliases.append(text)
        for s,p,o in triples:
            aliases.append(str(o))
        return aliases

    def get_descriptions(self,texts=[],triples=[]):
        descriptions = []
        for text in texts:
            pass
        for s,p,o in triples:
            pass
        return descriptions

        

    def _produce_blacklist_words(self):
        blacklist_words = manual_blacklist.copy()
        def split_inner(word):
            return word.lower().split(" ")

        for c_name in identifiers.external.cd_type_names.values():
            c_name = split_inner(c_name)
            blacklist_words = blacklist_words + c_name

        for c_role in identifiers.external.cd_role_dict.values():
            for role_name in c_role.values():
                r_name = split_inner(role_name)
                blacklist_words = blacklist_words + r_name
        return list(set(blacklist_words))