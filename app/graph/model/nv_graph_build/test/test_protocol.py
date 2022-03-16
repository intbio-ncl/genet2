import warnings
warnings.filterwarnings("ignore")
import unittest
import os
import sys
from rdflib import Graph,URIRef

sys.path.insert(0, os.path.join(".."))


from protocol_builder import produce_ontology_graph
curr_dir = os.path.dirname(os.path.realpath(__file__))
model_fn = os.path.join(curr_dir,"..","nv_protocol.xml")


class TestUtility(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_produce_identifiers(self):
        produce_ontology_graph  ()
        graph = Graph()
        graph.parse(model_fn)
        
        ec = list(graph.triples((URIRef("http://www.nv_ontology.org/Extract"),URIRef("http://www.w3.org/2002/07/owl#equivalentClass"),None)))[0][2]
        i = list(graph.triples((ec,URIRef("http://www.w3.org/2002/07/owl#intersectionOf"),None)))[0][2]


        first = list(graph.triples((i,URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#first'),None)))[0][2]
        rest = list(graph.triples((i,URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#rest'),None)))[0][2]
if __name__ == '__main__':
    unittest.main()

