import unittest
import os
import sys

from rdflib import RDF
sys.path.insert(0, os.path.join(".."))
sys.path.insert(0, os.path.join("..",".."))
sys.path.insert(0, os.path.join("..","..",".."))

from app.dashboards.builder.design import DesignBuilder
from app.graphs.neo_graph.nv_graph import NVGraph

curr_dir = os.path.dirname(os.path.realpath(__file__))
test_fn = os.path.join(curr_dir,"..","files","design","sbol","output.xml")
class TestGraph(unittest.TestCase):

    def setUp(self):
        self._wrapper = NVGraph()
        self._backup = self._wrapper.get_all_edges()
        self._wrapper.purge()
        self._wrapper.add_graph(test_fn)
        b = DesignBuilder(self._wrapper)
        b.set_full_view()
        self.d_graph = b.view

    def tearDown(self):
        self._wrapper.purge()
        if len(self._backup) > 0:
            for edge in self._backup:
                n = self._wrapper.add_node(edge.n)
                v = self._wrapper.add_node(edge.v)
                self._wrapper.add_edge(n,v,edge)
            self._wrapper.submit()

    def test_nodes(self):
        all_nodes = self._wrapper.get_all_nodes()
        for n in self.d_graph.nodes():
            self.assertIn(n,all_nodes)

    def test_edges(self):
        all_edges = self._wrapper.get_all_edges()
        for edge in self.d_graph.edges():
            self.assertIn(edge,all_edges)

    def test_in_edges(self):
        for n in self._wrapper.get_all_nodes():
            self.assertCountEqual(self._wrapper.edge_query(n), self.d_graph.out_edges(n))
    
    def test_merge_node(self):
        nodes = [*self.d_graph.nodes()]
        self.d_graph.merge_nodes(nodes[0],nodes[1:])
        self.assertEqual([nodes[0]],[*self.d_graph.nodes()])
        self.assertEqual([],[*self.d_graph.edges()])

def node_diff(list1,list2):
    diff = []
    for n,data in list1:
        for n1,data1 in list2:
            if n == n1 and data==data1:
                break
        else:
            diff.append((n,data))
    return diff

def edge_diff(list1,list2):
    diff = []
    for n,v,e,k in list1:
        for n1,v1,e1,k1 in list2:
            if n == n1 and v == v1 and e == e1 and k == k1:
                break
        else:
            diff.append((n,v,e,k))
    return diff

if __name__ == '__main__':
    unittest.main()
