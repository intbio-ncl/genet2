import unittest
import os
import sys

sys.path.insert(0, os.path.join(".."))
sys.path.insert(0, os.path.join("..",".."))
sys.path.insert(0, os.path.join("..","..",".."))

from app.visualiser.builder.design import DesignBuilder
from app.graph.world_graph import WorldGraph

curr_dir = os.path.dirname(os.path.realpath(__file__))
test_fn = os.path.join(curr_dir,"..","files","output.xml")
class TestProjectGraph(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        self.gn = "test_graph1"
        self._wrapper = WorldGraph()
        self._wrapper.add_design(test_fn,self.gn)
        self._driver = self._wrapper.driver
        b = DesignBuilder(self._wrapper)
        b.set_design_names(self.gn)
        b.set_full_view()
        self.d_graph = b.view

    @classmethod
    def tearDownClass(self):
        self._wrapper.remove_design(self.gn)

if __name__ == '__main__':
    unittest.main()
