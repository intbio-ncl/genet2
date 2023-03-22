import sys
import os
import unittest
from rdflib import URIRef
sys.path.insert(0, os.path.join(".."))
sys.path.insert(0, os.path.join("..",".."))
sys.path.insert(0, os.path.join("..","..",".."))
sys.path.insert(0, os.path.join("..","..","..",".."))
from app.graph.world_graph import WorldGraph
from app.enhancer.enhancer import Enhancer
from app.graph.utility.graph_objects.node import Node
from app.graph.utility.model.model import model
from app.graph.truth_graph.modules.interaction import InteractionModule
from app.enhancer.enhancements.interaction.text_extraction import TruthTextExtraction
from app.enhancer.enhancements.interaction.text_extraction import DesignTextExtraction
from app.converter.utility.graph import SBOLGraph
curr_dir = os.path.dirname(os.path.realpath(__file__))


class TestEnhancements(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.wg = WorldGraph()
        self.tg = self.wg.truth
        self.enhancer = Enhancer(self.wg)
        self.im = InteractionModule(self.wg.truth)

    @classmethod
    def tearDownClass(self):
        pass
    
    def test_protein_production_enhancements_tg_auto(self):
        record = ["https://synbiohub.org/public/igem/BBa_K1725000/1"]
        for r in record:
            r = URIRef(r)
            rec = SBOLGraph(self.enhancer._miner.get_external(r))
            md = rec.get_metadata(r)
            self.tg.add_node(r,model.identifiers.objects.dna,description=md)

        ppe = TruthTextExtraction(self.wg,self.enhancer._miner)
        pre_e = self.tg.edges()
        ppe.enhance()
        post_e = self.tg.edges()
        diff = list(set(post_e) - set(pre_e))
        self.assertEqual(len(diff),2)

        for i in range(0,20):
            for e in diff:
                self.tg.interactions.negative(e.n,e.v,e.get_type())