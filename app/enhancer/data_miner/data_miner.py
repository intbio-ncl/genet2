from app.enhancer.data_miner.language.analyser import LanguageAnalyser
from app.enhancer.data_miner.database.handler import DatabaseHandler
from app.enhancer.data_miner.ontology.handler import OntologyHandler
from app.enhancer.data_miner.graph_analyser.analyser import GraphAnalyser
from app.enhancer.data_miner.utility.identifiers import identifiers
from rdflib import RDF
s_seq = identifiers.predicates.sequence
s_ele = identifiers.predicates.elements
s_cd = identifiers.objects.component_definition

class DataMiner:
    def __init__(self):
        self._database = DatabaseHandler()
        self._language = LanguageAnalyser()
        self._ontology = OntologyHandler()
        self._graph_analyser = GraphAnalyser(self._database)

    def is_reference(self,uri):
        return self._database.is_record(uri)

    def get_external(self,name):
        return self._database.get(name)
    
    def get_graph_subject(self,graph,fragments=None):
        return self._graph_analyser.get_subject(graph,fragments)

    def query_external(self,query,lazy=False):
        return self._database.query(query,lazy=lazy)

    def get_descriptors(self,descriptions):
        return self._language.get_subjects(descriptions)

    def full_sequence_match(self,sequence):
        matches = self._database.sequence_search(sequence)
        if matches is None:
            return None
        if len(matches) == 1:
            print(matches)
            return list(matches.keys())[0]
        # When a part has multiple names of 
        # is referenced in multiple records.
        cds = []
        for uri,match in matches.items():
            r = self._database.get(uri)
            cds += r.triples((None,RDF.type,s_cd))
        return str(max(set(cds), key=cds.count)[0])

    def partial_sequence_match(self,sequence):
        matches = self._database.sequence_search(sequence,0.8)
        if matches is None or matches == {}:
            return {}
        return matches

    def get_root_subjects(self,graphs,e_type=None,fragments=None):
        return self._graph_analyser.get_roots(graphs,e_type=e_type,fragments=fragments)

    def get_leaf_subjects(self,graphs,e_type=None,fragments=None):
        return self._graph_analyser.get_leafs(graphs,e_type=e_type,fragments=fragments)

    def mine_explicit_reference(self,descriptions):
        '''
        Very basic mine, only description with a single 
        word will be taken as a potential reference.
        '''
        # I wonder if a general trash word prune from the langauge object could be used.
        for description in descriptions:
            if len(description.split(" ")) != 1:
                continue
            record = self._database.get(description)
            if record is not None:
                return self.get_graph_subject(record,[description])
        return None

    def mine_implicit_reference(self,descriptions):
        pass

