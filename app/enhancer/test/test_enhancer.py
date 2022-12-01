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

    def test_canonicalise_graph_automated(self):
        fn = os.path.join("test","files","canonicalise_get.xml")
        gn = "test_canonicalise_get"
        try:
            self.wg.remove_design(gn)
        except Exception:
            pass

        convert(fn,self.wg.driver,gn)
        dg = self.wg.get_design(gn)
        pre_pes = dg.get_physicalentity()
        self.enhancer.canonicalise_graph(gn,mode="automated")
        post_pes = dg.get_physicalentity()
        diff = list(set(post_pes) - set(pre_pes))
        self.assertEqual(len(diff),len(pre_pes))
        for d in diff:
            response = requests.get(d)
            self.assertTrue(response.status_code == 200)
        dg.drop()

    def test_canonicalise_graph_semi_automated(self):
        fn = os.path.join("test","files","test_canonicalise_graph_semi_automated.xml")
        gn = "test_canonicalise_graph_semi_automated"
        try:
            self.wg.remove_design(gn)
        except Exception:
            pass
        convert(fn,self.wg.driver,gn)
        dg = self.wg.get_design(gn)
        pre_pes = dg.get_physicalentity()
        standardised_uri = "https://synbiohub.org/public/igem/BBa_B0034/1"
        self.wg.truth.synonyms.positive(standardised_uri,"unknown_uri")
        reps,fback = self.enhancer.canonicalise_graph(gn,mode="semi_automated")
        ks = list(reps.keys())[0:2]
        valids = {k:reps[k] for k in ks}
        self.enhancer.apply_cannonical(valids,gn,fback)
        post_pes = dg.get_physicalentity()
        diff = list(set(post_pes) - set(pre_pes))
        self.assertEqual(len(diff),len(pre_pes))
        for d in diff:
            response = requests.get(d)
            self.assertTrue(response.status_code == 200)
        res = self.wg.truth.edges(n=standardised_uri,v="unknown_uri")
        self.assertEqual(len(res),1)
        self.assertEqual(res[0]["http://purl.obolibrary.org/obo/NCIT_C49020"],"10") 

        self.wg.truth.synonyms.negative(standardised_uri,"unknown_uri")
        self.wg.truth.synonyms.negative(standardised_uri,"unknown_uri")
        dg.drop()
    
    def test_canonicalise_entity_automated(self):
        fn = os.path.join("test","files","canonicalise_get.xml")
        gn = "test_canonicalise_get"
        try:
            self.wg.remove_design(gn)
        except Exception:
            pass
        convert(fn,self.wg.driver,gn)
        dg = self.wg.get_design(gn)
        pre_pes = dg.get_physicalentity()

        for p in pre_pes:
            res = self.enhancer.canonicalise_entity(p,gn)
        post_pes = dg.get_physicalentity()
        diff = list(set(post_pes) - set(pre_pes))
        self.assertEqual(len(diff),len(pre_pes))
        for d in diff:
            response = requests.get(d)
            self.assertTrue(response.status_code == 200)
        dg.drop()

    def test_canonicalise_entity_semi_automated(self):
        fn = os.path.join("test","files","test_canonicalise_graph_semi_automated.xml")
        gn = "test_canonicalise_graph_semi_automated"
        try:
            self.wg.remove_design(gn)
        except Exception:
            pass
        convert(fn,self.wg.driver,gn)
        dg = self.wg.get_design(gn)
        pre_pes = dg.get_physicalentity()
        standardised_uri = "https://synbiohub.org/public/igem/BBa_B0034/1"
        self.wg.truth.synonyms.positive(standardised_uri,"unknown_uri")

        reps,fback = self.enhancer.canonicalise_entity(pre_pes[0],gn,mode="semi_automated")
        ks = list(reps.keys())[0:2]
        valids = {k:reps[k] for k in ks}
        self.enhancer.apply_cannonical(valids,gn,fback)
        post_pes = dg.get_physicalentity()
        diff = list(set(post_pes) - set(pre_pes))
        self.assertEqual(len(diff),len(pre_pes))
        for d in diff:
            response = requests.get(d)
            self.assertTrue(response.status_code == 200)
        res = self.wg.truth.edges(n=standardised_uri,v="unknown_uri")
        self.assertEqual(len(res),1)
        self.assertEqual(res[0]["http://purl.obolibrary.org/obo/NCIT_C49020"],"10") 

        self.wg.truth.synonyms.negative(standardised_uri,"unknown_uri")
        self.wg.truth.synonyms.negative(standardised_uri,"unknown_uri")
        dg.drop()

    def test_canonicalise_entity_semi_automated_potential(self):
        fn = os.path.join("test","files","test_canonicalise_graph_semi_automated_potential.xml")
        gn = "test_canonicalise_graph_semi_automated"
        try:
            self.wg.remove_design(gn)
        except Exception:
            pass
        convert(fn,self.wg.driver,gn)
        dg = self.wg.get_design(gn)
        pre_pes = dg.get_physicalentity()
        standardised_uri = "https://synbiohub.org/public/igem/BBa_B0034/1"
        self.wg.truth.synonyms.positive(standardised_uri,"unknown_uri")

        reps,fback = self.enhancer.canonicalise_entity(pre_pes[0],gn,mode="semi_automated")
        ks = list(reps.keys())[0:2]
        valids = {k:reps[k] for k in ks}
        for k,v in reps.items():
            print(k,v)
        exit()
        self.enhancer.apply_cannonical(valids,gn,fback)
        post_pes = dg.get_physicalentity()
        diff = list(set(post_pes) - set(pre_pes))
        self.assertEqual(len(diff),len(pre_pes))
        for d in diff:
            response = requests.get(d)
            self.assertTrue(response.status_code == 200)
        res = self.wg.truth.edges(n=standardised_uri,v="unknown_uri")
        self.assertEqual(len(res),1)
        self.assertEqual(res[0]["http://purl.obolibrary.org/obo/NCIT_C49020"],"10") 

        self.wg.truth.synonyms.negative(standardised_uri,"unknown_uri")
        self.wg.truth.synonyms.negative(standardised_uri,"unknown_uri")
        dg.drop()


    def test_seed_graph(self):
        self.enhancer.seed_truth_graph()
