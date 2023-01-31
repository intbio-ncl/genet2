import sys
import os
import unittest
import requests
sys.path.insert(0, os.path.join(".."))
sys.path.insert(0, os.path.join("..",".."))
sys.path.insert(0, os.path.join("..","..",".."))
sys.path.insert(0, os.path.join("..","..","..",".."))
from app.graph.world_graph import WorldGraph
from app.enhancer.enhancer import Enhancer
from converter.sbol_convert import convert
curr_dir = os.path.dirname(os.path.realpath(__file__))
fn = os.path.join("test","files","nor_full.xml")

class TestEnhancer(unittest.TestCase):
    
    @classmethod
    def setUpClass(self):
        self.gn = "test_enhancer"
        self.wg = WorldGraph()
        self.enhancer = Enhancer(self.wg)

    @classmethod
    def tearDownClass(self):
        self.wg.remove_design(self.gn)

    # --- Evaluate ---
    def test_evaluate_design(self):
        pass
    
    def test_get_evaluators(self):
        pass

    # --- Truth ---
    def test_seed_truth_graph(self):
        self.enhancer.seed_truth_graph()

    def test_enhance_truth_graph(self):
        self.enhancer.enhance_truth()

    def test_apply_truth_graph(self):
        pass

    # --- Design --- 
    def test_enhance_truth_graph(self):
        pass

    def test_apply_truth_graph(self):
        pass