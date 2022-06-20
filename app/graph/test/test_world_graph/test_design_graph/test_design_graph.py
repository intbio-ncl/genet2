import sys
import os
import unittest

sys.path.insert(0, os.path.join(".."))
sys.path.insert(0, os.path.join("..",".."))
sys.path.insert(0, os.path.join("..","..",".."))
sys.path.insert(0, os.path.join("..","..","..",".."))
sys.path.insert(0, os.path.join("..","..","..","..",".."))
from world_graph import WorldGraph
curr_dir = os.path.dirname(os.path.realpath(__file__))

fn = os.path.join(curr_dir,"..","..","files","nor_full.xml")
class TestDesignGraph(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.gn = "test_dg"
        self.wg = WorldGraph()
        self.dg = self.wg.add_design(fn,self.gn)

    @classmethod
    def tearDownClass(self):
        self.wg.remove_design(self.gn)

    def test_drop(self):
        self.wg.remove_design(self.gn)
        dg = self.wg.get_design(self.gn)
        self.assertEqual(dg.nodes(),[])
        self.assertEqual(dg.edges(),[])
        self.wg.add_design(fn,self.gn)

    def test_get_children(self):
        pes = self.dg.get_physicalentity()
        for entity in pes:
            for edge in self.dg.get_children(entity):
                self.assertIn(edge.v,pes)
                self.assertEqual(edge.n,entity)

    def test_get_parents(self):
        pes = self.dg.get_physicalentity()
        for entity in pes:
            for edge in self.dg.get_parents(entity):
                self.assertIn(edge.n,pes)
                self.assertEqual(edge.v,entity)


        
        


