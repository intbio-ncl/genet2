import sys
import os
import unittest
sys.path.insert(0, os.path.join(".."))
sys.path.insert(0, os.path.join("..",".."))
sys.path.insert(0, os.path.join("..","..",".."))
sys.path.insert(0, os.path.join("..","..","..",".."))
from app.graph.world_graph import WorldGraph
from app.enhancer.enhancer import Enhancer
from app.graph.utility.graph_objects.node import Node
from app.graph.utility.model.model import model
from app.graph.truth_graph.modules.interaction import InteractionModule
from app.enhancer.enhancements.interaction.protein_production import TruthProteinProduction
from app.enhancer.enhancements.interaction.protein_production import DesignProteinProduction
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
        nodes = [Node("https://synbiohub.org/public/igem/my_fake_uri/1",model.identifiers.objects.cds),
                 Node("https://synbiohub.org/public/igem/my_fake_uri_protein/1",model.identifiers.objects.protein),
                 Node("https://synbiohub.org/public/igem/my_fake_uri_protein_generation/1",model.identifiers.objects.genetic_production),
                 Node("https://synbiohub.org/public/igem/my_fake_uri2/1",model.identifiers.objects.cds)]
        [self.tg.add_node(n) for n in nodes]
        edges = [(nodes[2],nodes[0],model.identifiers.predicates.template),
                (nodes[2],nodes[1],model.identifiers.predicates.product)]
        [self.im.positive(*e) for e in edges]
        ppe = TruthProteinProduction(self.wg,self.enhancer._miner)
        pre_e = self.tg.edges()
        ppe.enhance()
        post_e = self.tg.edges()
        diff = list(set(post_e) - set(pre_e))
        self.assertEqual(len(diff),2)

        for i in range(0,20):
            for e in diff:
                self.tg.interactions.negative(e.n,e.v,e.get_type())
        [self.im.negative(*e) for e in edges]


    def test_protein_production_enhancements_tg_manual(self):
        nodes = [Node("https://synbiohub.org/public/igem/my_fake_uri/1",model.identifiers.objects.cds),
                 Node("https://synbiohub.org/public/igem/my_fake_uri_protein/1",model.identifiers.objects.protein),
                 Node("https://synbiohub.org/public/igem/my_fake_uri_protein_generation/1",model.identifiers.objects.genetic_production),
                 Node("https://synbiohub.org/public/igem/my_fake_uri2/1",model.identifiers.objects.cds)]
        [self.tg.add_node(n) for n in nodes]
        edges = [(nodes[2],nodes[0],model.identifiers.predicates.template),
                (nodes[2],nodes[1],model.identifiers.predicates.product)]
        [self.im.positive(*e) for e in edges]
        ppe = TruthProteinProduction(self.wg,self.enhancer._miner)
        pre_e = self.tg.edges()
        res = ppe.enhance(mode="manual")
        for k,v in res.items():
            for k1,v1 in v.items():
                v1["apply"] = True
        ppe.apply(res)
        post_e = self.tg.edges()
        diff = list(set(post_e) - set(pre_e))
        self.assertEqual(len(diff),2)
        for i in range(0,20):
            for e in diff:
                self.tg.interactions.negative(e.n,e.v,e.get_type())
        [self.im.negative(*e) for e in edges]


    def test_protein_production_enhancements_d_auto(self):
        gn = "test_protein_production_enhancements_d_auto"
        nodes = [Node("https://synbiohub.org/public/igem/my_fake_uri/1",model.identifiers.objects.cds),
                 Node("https://synbiohub.org/public/igem/my_fake_uri_protein/1",model.identifiers.objects.protein),
                 Node("https://synbiohub.org/public/igem/my_fake_uri_protein_generation/1",model.identifiers.objects.genetic_production),
                 Node("https://synbiohub.org/public/igem/my_fake_uri2/1",model.identifiers.objects.cds)]
        dg = self.wg.get_design(gn)
        nodes = [dg.add_node(n.get_key(),n.get_type()) for n in nodes]
        edges = [(nodes[2],nodes[0],model.identifiers.predicates.template),
                (nodes[2],nodes[1],model.identifiers.predicates.product)]
        dg.add_edges(edges)
        ppe = DesignProteinProduction(self.wg,self.enhancer._miner)
        pre_e = dg.edges()
        ppe.enhance(dg.name)
        post_e = dg.edges()
        diff = list(set(post_e) - set(pre_e))
        self.assertEqual(len(diff),2)
        for i in range(0,20):
            for e in diff:
                self.tg.interactions.negative(e.n,e.v,e.get_type())
        self.wg.remove_design(gn)


    def test_protein_production_enhancements_d_manual(self):
        gn = "test_protein_production_enhancements_d_auto"
        nodes = [Node("https://synbiohub.org/public/igem/my_fake_uri/1",model.identifiers.objects.cds),
                 Node("https://synbiohub.org/public/igem/my_fake_uri_protein/1",model.identifiers.objects.protein),
                 Node("https://synbiohub.org/public/igem/my_fake_uri_protein_generation/1",model.identifiers.objects.genetic_production),
                 Node("https://synbiohub.org/public/igem/my_fake_uri2/1",model.identifiers.objects.cds)]
        dg = self.wg.get_design(gn)
        nodes = [dg.add_node(n.get_key(),n.get_type()) for n in nodes]
        edges = [(nodes[2],nodes[0],model.identifiers.predicates.template),
                (nodes[2],nodes[1],model.identifiers.predicates.product)]
        dg.add_edges(edges)
        ppe = DesignProteinProduction(self.wg,self.enhancer._miner)
        pre_e = dg.edges()
        res = ppe.enhance(dg.name,mode="manual")
        for k,v in res.items():
            for k1,v1 in v.items():
                v1["apply"] = True
        ppe.apply(res,gn)
        post_e = dg.edges()
        diff = list(set(post_e) - set(pre_e))
        self.assertEqual(len(diff),2)
        for i in range(0,20):
            for e in diff:
                self.tg.interactions.negative(e.n,e.v,e.get_type())
        self.wg.remove_design(gn)