
import os
import atexit
import rdflib
from enum import Enum

language_graph_map = os.path.join(os.path.dirname(os.path.realpath(__file__)),"ontology_map.xml")

class Identifiers(Enum):
    namespace = rdflib.URIRef("http://ontology_graph/")
    synonym_subject_type = rdflib.URIRef(namespace + "OntologyIdentifier")
    synonym_predicate = rdflib.URIRef(namespace + "synonym")
    definite_synonym_predicate = rdflib.URIRef(namespace + "definiteSynonym")
    potential_synonym_predicate = rdflib.URIRef(namespace + "potentialSynonym")
    definition_predicate = rdflib.URIRef(namespace + "definition")
    comment_predicate = rdflib.URIRef(namespace + "comment")
    label_predicate = rdflib.URIRef(namespace + "label")
    xref_predicate = rdflib.URIRef(namespace + "hasdbxref")
    
class OntologyTermMap:
    def __init__(self,server):
        self.server = server
        
        if not os.path.isfile(language_graph_map):
            self.language_graph = self._build_graph()
        else:
            self.language_graph = rdflib.Graph()
            self.language_graph.parse(language_graph_map)

        atexit.register(self._save_graph) 
    
    def search(self,pattern):
        return self.language_graph.triples(pattern)

    def add(self,triples):
        self.language_graph.add(triples)

    def _build_graph(self):
        '''
        Aim: For each propietry predicate find predicates within the onotlogy that they can be mapped against.
        '''
        predicates = {Identifiers.definite_synonym_predicate.value : ["synonym"],
                      Identifiers.definition_predicate.value : ["definition","iao_0000115"],
                      Identifiers.comment_predicate.value : ["comment"],
                      Identifiers.label_predicate.value : ["label"],
                      Identifiers.xref_predicate.value: ["hasdbxref"]}
        objects = {Identifiers.potential_synonym_predicate.value : ["synonym"]}

        g = rdflib.Graph()
        for ontology_code in self.server.get_ontology_codes():
            for identifier,values in predicates.items():
                for v in values:
                    v = rdflib.Literal(v)
                    triples = self._get_partial_predicate(v,ontology_code)
                    for s,p,o in triples:   
                        subject = rdflib.URIRef(Identifiers.namespace.value + ontology_code)
                        g.add((subject,identifier,p))

            for identifier,values in objects.items():
                for v in values:
                    v = rdflib.Literal(v)
                    triples = self.server.select((None,None,v),ontology_code=ontology_code)
                    for s,p,o in triples:   
                        subject = rdflib.URIRef(Identifiers.namespace.value + ontology_code)
                        g.add((subject,identifier,p))
        return g

    def _save_graph(self):
        return self.language_graph.serialize(destination=language_graph_map, format="xml")

    def _get_partial_predicate(self,partial_predicate,ontology_code):
        server_uris = self.server.get_server_uri(ontology_code)
        results = []
        for server_uri in server_uris:
            query = self.server.query_builder.get_partial_predicates(partial_predicate,server_uri)
            result = self.server._run_query(str(query))
            if result is not None:
                results = results + self.server._normalise_results(result,query.triples)
        return results