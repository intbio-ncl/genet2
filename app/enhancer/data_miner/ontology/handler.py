
from app.enhancer.data_miner.ontology.mediator import OntologyMediator
from app.enhancer.data_miner.ontology.ontology_term_map import Identifiers

synonym_subject_type = Identifiers.synonym_subject_type.value
synonym_predicate = Identifiers.synonym_predicate.value
definite_synonym = Identifiers.definite_synonym_predicate.value
potential_synonym = Identifiers.potential_synonym_predicate.value

class OntologyHandler:
    def __init__(self,offline=False):       
        self.is_offline = offline
        if not offline:
            self.ontology_mediator = OntologyMediator()
        
    def get_synonyms(self,identifier):
        definite_synonyms  = self.ontology_mediator.search((identifier,definite_synonym,None))
        potential_synonyms = self.ontology_mediator.search((identifier,potential_synonym,None))
        definite_synonyms = [s[2] for s in definite_synonyms]
        potential_synonyms = [s[2] for s in potential_synonyms if s[2] not in definite_synonyms]
        return list(set(definite_synonyms)),list(set(potential_synonyms))

    def get_descriptor(self,descriptions):
        definite_descriptors = [s for s,p,o in self.ontology_mediator.search((None,definite_synonym,descriptions))]
        potential_descriptors = self.ontology_mediator.search((None,potential_synonym,descriptions))
        potential_descriptors = [s for s,p,o in potential_descriptors if s not in definite_descriptors.keys()]
        return definite_descriptors,potential_descriptors


    def unmask(self,identifier):
        unmask = self.ontology_mediator.unmask_uri(identifier)
        return unmask
    
    def mask(self,identifer):
        mask = self.ontology_mediator.mask_uri(identifer)
        return mask

