import unittest
import os
import sys
import re

from rdflib import RDF,OWL,BNode
sys.path.insert(0, os.path.join(".."))

from converters.design_handler import convert as m_convert
from utility.identifiers import produce_identifiers

curr_dir = os.path.dirname(os.path.realpath(__file__))
model_fn = os.path.join(curr_dir,"..","utility","nv_design.xml")


class TestUtility(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_produce_identifiers(self):
        graph = m_convert(model_fn)
        identifiers = produce_identifiers(graph)
        
        for n,v,e in graph.search((None,RDF.type,OWL.Class)):
            n_key = n[1]["key"]
            if isinstance(n_key, BNode):
                continue
            n_key_name = _get_name(n_key)
            res = eval(f'identifiers.objects.{n_key_name}')
            self.assertEqual(res, n_key)

        for n,v,e in graph.search((None,OWL.hasValue,None)):
            n_key = n[1]["key"]
            if isinstance(n_key, BNode):
                continue
            n_key_name = _get_name(n_key)
            res = eval(f'identifiers.roles.{n_key_name}')
            self.assertEqual(res, n_key)
        

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
if __name__ == '__main__':
    unittest.main()

