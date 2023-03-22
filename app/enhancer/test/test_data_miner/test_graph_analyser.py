import unittest
import sys,os
import re
import requests
from rdflib import Graph,RDF


sys.path.insert(0, os.path.join("..","..","..","..",".."))
sys.path.insert(0, os.path.join("..","..","..",".."))
sys.path.insert(0, os.path.join("..","..",".."))
sys.path.insert(0, os.path.join("..",".."))
from app.converter.utility.identifiers import identifiers
from app.graph.utility.model.model import model
from app.enhancer.data_miner.data_miner import DataMiner
class TestGraphAnalyser(unittest.TestCase):
    def setUp(self):
        self.dm = DataMiner()
        self.analyser = self.dm._graph_analyser

    def tearDown(self):
        pass
        
    def test_get_subject(self):
        test_file = os.path.join("files","Model_0x19_collection.xml")
        g = Graph()
        g.parse(test_file)
        for s,p,o in g.triples((None,RDF.type,identifiers.objects.component_definition)):
            self.assertEqual(s,self.analyser.get_subject(g,[_get_name(s)]))


    def test_get_roots(self):
        e_type = model.identifiers.objects.promoter
        fragments = ["pveg"]
        graphs = [self.dm.get_external(r) for r in list(self.dm.query_external(fragments[0],lazy=True))[0]]
        for r in self.analyser.get_roots(graphs,e_type,fragments):
            response = requests.get(r)
            self.assertTrue(response.status_code == 200)
    
    def test_get_leafs(self):
        e_type = model.identifiers.objects.promoter
        fragments = ["pveg"]
        graphs = [self.dm.get_external(r) for r in list(self.dm.query_external(fragments[0],lazy=True))[0]]
        for r in self.analyser.get_leafs(graphs,e_type,fragments):
            print(r)
            response = requests.get(r)
            self.assertTrue(response.status_code == 200)


def _get_name(subject):
    split_subject = _split(subject)
    if len(split_subject[-1]) == 1 and split_subject[-1].isdigit():
        return split_subject[-2]
    elif len(split_subject[-1]) == 3 and _isfloat(split_subject[-1]):
        return split_subject[-2]
    else:
        return split_subject[-1]


def _split(uri):
    return re.split('#|\/|:', uri)


def _isfloat(x):
    try:
        float(x)
        return True
    except ValueError:
        return False