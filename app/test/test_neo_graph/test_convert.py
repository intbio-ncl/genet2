import sys
import os
import copy
sys.path.insert(0, os.path.join(".."))
sys.path.insert(0, os.path.join("..",".."))
sys.path.insert(0, os.path.join("..","..",".."))
import unittest
from app.graphs.neo_graph.nv_graph import NVGraph
from app.graphs.neo_graph.converter.design.utility.graph import SBOLGraph
curr_dir = os.path.dirname(os.path.realpath(__file__))

test_fn = os.path.join(curr_dir,"..","files","output.xml")

class TestConvertDesign(unittest.TestCase):
    def setUp(self):
        self._wrapper = NVGraph()
        self._rdf = SBOLGraph(test_fn)
        self._backup = self._wrapper.get_all_edges()
        self._wrapper.purge()
        self._wrapper.add_graph(test_fn)

    def tearDown(self):
        self._wrapper.purge()
        if len(self._backup) > 0:
            for edge in self._backup:
                n = self._wrapper.add_node(edge.n)
                v = self._wrapper.add_node(edge.v)
                self._wrapper.add_edge(n,v,edge)
            self._wrapper.submit()

if __name__ == '__main__':
    unittest.main()
