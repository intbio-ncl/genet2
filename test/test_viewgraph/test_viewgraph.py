import unittest
import os
import sys

sys.path.insert(0, os.path.join(".."))
sys.path.insert(0, os.path.join("..",".."))
sys.path.insert(0, os.path.join("..","..",".."))

from app.visualiser.builder.design import DesignBuilder
from app.graph.world_graph import WorldGraph
from app.converter.sbol_convert import convert

curr_dir = os.path.dirname(os.path.realpath(__file__))
test_fn = os.path.join(curr_dir,"..","files","output.xml")
class TestViewGraph(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.gn = "test_graph1"
        self._wrapper = WorldGraph()
        self._wrapper.remove_design(self.gn)
        convert(test_fn,self._wrapper.driver,self.gn)
        self._driver = self._wrapper.driver
        b = DesignBuilder(self._wrapper)
        b.set_design_names(self.gn,"Union")
        b.set_full_view()
        b.build()
        self.d_graph = b.view

    @classmethod
    def tearDownClass(self):
        self._wrapper.remove_design(self.gn)

    def test_nodes(self):
        all_nodes = self._driver.node_query(graph_name=self.gn)
        for n in self.d_graph.nodes():
            self.assertIn(n,all_nodes)

    def test_edges(self):
        all_edges = self._driver.edge_query(e_props={"graph_name" : self.gn})
        for edge in self.d_graph.edges():
            self.assertIn(edge,all_edges)

    def test_in_edges(self):
        for n in self._driver.node_query(graph_name=self.gn):
            self.assertCountEqual(self._driver.edge_query(v=n,e_props={"graph_name" : self.gn}), 
                                  self.d_graph.in_edges(n.id))

    def test_merge_node(self):
        nodes = [*self.d_graph.nodes()]
        self.d_graph.merge_nodes(nodes[0],nodes[1:])
        self.assertEqual([nodes[0]],[*self.d_graph.nodes()])
        self.assertEqual([],[*self.d_graph.edges()])

    def test_has_edge(self):
        for e in self._driver.edge_query(e_props={"graph_name" : self.gn}):
            self.assertTrue(self.d_graph.has_edge(e))


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
