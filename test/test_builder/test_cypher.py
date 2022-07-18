import unittest
import os
import sys

sys.path.insert(0, os.path.join(".."))
sys.path.insert(0, os.path.join("..",".."))
sys.path.insert(0, os.path.join("..","..",".."))

from app.visualiser.builder.cypher import CypherBuilder
from app.graph.world_graph import WorldGraph

curr_dir = os.path.dirname(os.path.realpath(__file__))

class TestViews(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.gn = "test_builder_views"
        self.wg = WorldGraph()
        self.builder = CypherBuilder(self.wg)

    @classmethod
    def tearDownClass(self):
        pass
    
    def test_cypher(self):
        cypher_qry = "match (n) return n Limit 25"
        self.builder.set_cypher_view()
        dt = self.builder.build(cypher_qry,True)
        graph = self.builder.view
        self.assertTrue(len(list(graph.nodes())) <= 25)
        self.assertTrue(len(dt) == 25)
            
if __name__ == '__main__':
    unittest.main()
