import unittest
import os
import sys
from random import sample
from rdflib import RDF,BNode,URIRef

sys.path.insert(0, os.path.join(".."))
sys.path.insert(0, os.path.join("..",".."))
sys.path.insert(0, os.path.join("..","..",".."))

from app.dashboards.builder.projection import ProjectionBuilder
from app.graphs.neo_graph.nv_graph import NVGraph

curr_dir = os.path.dirname(os.path.realpath(__file__))
test_fn = os.path.join(curr_dir,"..","files","design","sbol","nor_full.xml")

class TestProjectBuilder(unittest.TestCase):
    def setUp(self):
        self._wrapper = NVGraph()
        self._backup = self._wrapper.get_all_edges()
        self._wrapper.purge()
        self._wrapper.add_graph(test_fn)
        self.builder = ProjectionBuilder(self._wrapper)
        self.builder.set_full_view()

    def tearDown(self): 
        self._wrapper.purge()
        if len(self._backup) > 0:
            for edge in self._backup:
                n = self._wrapper.add_node(edge.n)
                v = self._wrapper.add_node(edge.v)
                self._wrapper.add_edge(n,v,edge)
            self._wrapper.submit()

    def test_get_project_info(self):
        gn1 = "test1"
        try:
            self._wrapper.project.drop(gn1)
        except Exception:
            pass
        res = self.builder.project_preset(gn1,"hierarchy")
        self.builder.set_projection_view(gn1)
        view = self.builder.view
        nodes = self.builder.get_project_info()
    
    def test_get_procedure_info(self):
        gn1 = "test1"
        try:
            self._wrapper.project.drop(gn1)
        except Exception:
            pass
        res = self.builder.project_preset(gn1,"hierarchy")
        self.builder.set_projection_view(gn1)
        view = self.builder.view
        struct = self.builder.get_procedures_info()

        
def diff(list1,list2):
    diff = []
    for n,v,e in list1:
        for n1,v1,e1 in list2:
            if n == n1 and v == v1 and e == e1:
                break
        else:
            diff.append((n,v,e,k))
    return diff


if __name__ == '__main__':
    unittest.main()
