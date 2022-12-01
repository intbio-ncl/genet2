import sys
import os
import unittest
sys.path.insert(0, os.path.join(".."))
sys.path.insert(0, os.path.join("..",".."))
sys.path.insert(0, os.path.join("..","..",".."))
sys.path.insert(0, os.path.join("..","..","..",".."))
from app.graph.world_graph import WorldGraph
from app.enhancer.enhancer import Enhancer

class TestEnhancer(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.gn = "test_enhancer"
        self.wg = WorldGraph()
        self.enhancer = Enhancer(self.wg)

    @classmethod
    def tearDownClass(self):
        self.wg.remove_design(self.gn)

    def test_tg_enhancements(self):
        self.enhancer.expand_truth_graph()
