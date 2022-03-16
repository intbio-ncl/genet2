import re
import os
import copy 
from pathlib import Path

import rdflib
from pysbolgraph.SBOL2Serialize import serialize_sboll2
from pysbolgraph.SBOL2Graph import SBOL2Graph

rdf_type = rdflib.RDF.type
class RDFGraphWrapper:
    def __init__(self, graph = None):
        if isinstance(graph,RDFGraphWrapper):
            self.graph = copy.deepcopy(graph.graph)
        elif isinstance(graph,rdflib.Graph):
            self.graph = copy.deepcopy(graph)
        else:
            self.graph = rdflib.Graph()
            if graph is not None:
                self.graph.load(graph)

    def __iter__(self):
        for x in self.graph:
            yield x
            
    def __len__(self):
        return len(self.graph)

    def add(self,triples):
        '''
        Given a single or list of triples add each triple to graph.
        '''
        if isinstance(triples, list):
            for s,p,o in triples:
                self.graph.add((rdflib.URIRef(s),rdflib.URIRef(p),o))
        elif isinstance(triples, tuple):
            if len(triples) != 3:
                raise ValueError("RDF Triples must contain three values.")
            self.graph.add(triples)
        else:
            raise ValueError("Input must be a triple or list of triples")

    def remove(self,triples):
        '''
        Given a single or list of triples add each triple to graph.
        '''
        if isinstance(triples, list):
            for triple in triples:
                if len(triple) != 3:
                    raise ValueError("RDF Triples must contain three values.")
                self.graph.remove((triple[0], triple[1], triple[2]))
        elif isinstance(triples, tuple):
            if len(triples) != 3:
                raise ValueError("RDF Triples must contain three values.")
            self.graph.remove((triples[0], triples[1], triples[2]))
        else:
            raise ValueError("Input must be a triple or list of triples")
        

    def replace(self,target,value):
        self.remove(target)
        self.add(value)
    
    def search(self,pattern,lazy=False):
        if lazy:
            for res in self.graph.triples(pattern):
                return res
            return None
        else:
            results = []
            for res in self.graph.triples(pattern):
                results.append(res)
            return results

    def triples(self,pattern):
        return self.graph.triples(pattern)
        
    def get_triples(self,subjects):
        triplepack = []
        for s,p,o in self.graph:
            if s in subjects:
                triplepack.append((s,p,o))
        return triplepack

    def has_triple(self,pattern):
        for _ in self.graph.triples(pattern):
            return True
        return False


    def get_possible_parents(self,child,relationship_predicate=None):
        '''
        Returns the possible parents of a triple.
        Parent - Child relationships are not definite if the relationship predicate is not known.
        Provide optional relationship predicate for definite parents.
        '''
        if isinstance(relationship_predicate,(list,set)):
            possible_parents = set()
            for r in relationship_predicate:
                possible_parents |= {s for (s, p, o) in self.search((None, r, child))}
            return possible_parents
        else:
            return self.search((None,relationship_predicate,child))

    def get_children(self,triple,relationship_predicate=None):
        '''
        Returns the possible parents of a triple.
        Parent - Child relationships are not definite if the relationship predicate is not known.
        Provide optional relationship predicate for definite children.
        '''
        if isinstance(triple,tuple):
            return self.search((triple[2],relationship_predicate,None))
        else:
            return self.search((triple,relationship_predicate,None))

    def get_type(self,subject):
        '''
        Return the possible object types based on the RDF.type property attached to uri.
        '''
        return {o for (s, p, o) in self.search((subject, rdf_type, None))}

    def get_identity_list(self):
        identities = []
        for s,p,o in self.graph:
            if s not in identities:
                identities.append(s)
        return identities

    def dump(self):
        '''
        Prints the full triplestore triple by triple.
        '''
        for s,p,o in self.graph:
            print(s,p,o)

    def load_graph(self,graph):
        '''
        Standard setter that sets the graph with a new input graph.
        '''
        self.graph = graph
    
    def sub_graph(self, triplepack=[]):
        new_graph = RDFGraphWrapper()
        new_graph.add(triplepack)
        return new_graph

    def add_graph(self,graph):
        if isinstance(graph,RDFGraphWrapper):
            self.graph = self.graph + graph.graph
        elif isinstance(graph, rdflib.Graph):
            self.graph = self.graph + graph
        else:
            self.graph.parse(graph)

    def save(self,filename,format="xml"):
        if format == 'sbolxml':
            pysbolG = SBOL2Graph()
            pysbolG += self.graph
            sbol = '<?xml version="1.0" encoding="UTF-8"?>\n'
            sbol = sbol + serialize_sboll2(pysbolG).decode("utf-8")
            Path(os.path.dirname(filename)).mkdir(parents=True, exist_ok=True)
            with open(filename, 'w+') as o:
                o.write(sbol)
        else:
            return self.graph.serialize(destination=filename, format=format)


    def serialise(self,serialisation = "rdfxml"):
        if serialisation == 'rdfxml':
            return self.graph.serialize(format='xml').decode("utf-8")
        elif serialisation == 'nt':
            return self.graph.serialize(format='nt').decode("utf-8")
        elif serialisation == 'n3':
            return self.graph.serialize(format='n3').decode("utf-8")
        elif serialisation == 'turtle':
            return self.graph.serialize(format='turtle').decode("utf-8")
        elif serialisation == 'sbolxml':
            pysbolG = SBOL2Graph()
            pysbolG += self.graph
            return serialize_sboll2(pysbolG).decode("utf-8")

def uri_ref(string):
    '''
    Elements added to a rdflib graph must be a URIRef object you can NOT just add primitives (string,int etc)
    '''
    return rdflib.URIRef(string)

def uri_literal(string):
    return rdflib.Literal(string)

