import sys
import os
import unittest
sys.path.insert(0, os.path.join(".."))
sys.path.insert(0, os.path.join("..",".."))
sys.path.insert(0, os.path.join("..","..",".."))
sys.path.insert(0, os.path.join("..","..","..",".."))
from app.graph.world_graph import WorldGraph
from app.enhancer.enhancer import Enhancer
curr_dir = os.path.dirname(os.path.realpath(__file__))
fn = os.path.join("test","files","nor_full.xml")

class TestOntology(unittest.TestCase):
    
    @classmethod
    def setUpClass(self):
        self.gn = "test_enhancer"
        self.wg = WorldGraph()
        #self.wg.add_design(fn,self.gn)
        self.enhancer = Enhancer(self.wg)

    @classmethod
    def tearDownClass(self):
        pass#self.wg.remove_design(self.gn)

    def test_canonise_graph(self):
        self.enhancer.cannonise_graph(self.gn)