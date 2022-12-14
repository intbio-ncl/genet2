import sys
import os
import unittest
sys.path.insert(0, os.path.join(".."))
sys.path.insert(0, os.path.join("..",".."))
sys.path.insert(0, os.path.join("..","..",".."))
sys.path.insert(0, os.path.join("..","..","..",".."))
from app.graph.world_graph import WorldGraph
from app.graph.truth_graph.modules.interaction import InteractionModule
from app.graph.utility.graph_objects.edge import Edge
from app.graph.utility.graph_objects.node import Node
from app.graph.utility.model.model import model

from app.enhancer.enhancer import Enhancer
from app.enhancer.enhancements.interaction import ProteinProductionEnhancement

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
    

    def test_protein_production_enhancements(self):
        nodes = [Node("https://synbiohub.org/public/igem/my_fake_uri/1",model.identifiers.objects.cds),
                 Node("https://synbiohub.org/public/igem/my_fake_uri_protein/1",model.identifiers.objects.protein),
                 Node("https://synbiohub.org/public/igem/my_fake_uri_protein_generation/1",model.identifiers.objects.genetic_production),
                 Node("https://synbiohub.org/public/igem/my_fake_uri2/1",model.identifiers.objects.cds)]
        [self.tg.add_node(n) for n in nodes]
        edges = [Edge(nodes[2],nodes[0],model.identifiers.predicates.template),
                Edge(nodes[2],nodes[1],model.identifiers.predicates.product)]
        [self.im.positive(e) for e in edges]
        ppe = ProteinProductionEnhancement(self.wg,self.enhancer._miner)
        pre_e = self.tg.edges()
        ppe.enhance(self.tg.name)
        post_e = self.tg.edges()
        diff = list(set(post_e) - set(pre_e))
        self.assertEqual(len(diff),2)
        for i in range(0,20):
            for e in diff:
                self.tg.interactions.negative(e)
        [self.im.negative(e) for e in edges]
        
    def test_tg_enhancements(self):
        self.enhancer.expand_truth_graph()
