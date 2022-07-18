import unittest
import os
import sys

sys.path.insert(0, os.path.join(".."))
sys.path.insert(0, os.path.join("..",".."))
sys.path.insert(0, os.path.join("..","..",".."))

from app.graph.world_graph import WorldGraph
from app.validator.pipelines.transitive import transitive_pipeline

curr_dir = os.path.dirname(os.path.realpath(__file__))
test_fn = os.path.join(curr_dir,"..","files","nor_full.xml")

class TestTransitive(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.gn = "test_trans"
        self.wg = WorldGraph()
        self.wg.add_design(test_fn,self.gn)
        

    @classmethod
    def tearDownClass(self):
        self._wrapper.remove_design(self.gn)

    def test_trans(self):
        rv = transitive_pipeline(self.wg)
        print(rv)

if __name__ == '__main__':
    unittest.main()
