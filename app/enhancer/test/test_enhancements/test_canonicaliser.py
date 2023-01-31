import sys
import os
import unittest
import rdflib
import re
import requests
sys.path.insert(0, os.path.join(".."))
sys.path.insert(0, os.path.join("..",".."))
sys.path.insert(0, os.path.join("..","..",".."))
sys.path.insert(0, os.path.join("..","..","..",".."))
from app.graph.utility.graph_objects.node import Node
from app.graph.utility.model.model import model
from app.graph.world_graph import WorldGraph
from app.enhancer.enhancer import Enhancer
from app.enhancer.enhancements.canonical.canonicaliser import DesignCanonicaliser
from converter.sbol_convert import convert
curr_dir = os.path.dirname(os.path.realpath(__file__))

class TestCanonicaliser(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.wg = WorldGraph()
        self.enhancer = Enhancer(self.wg)
        self.canonicaliser = DesignCanonicaliser(self.wg,self.enhancer._miner)
        self.tg = self.wg.truth

    @classmethod
    def tearDownClass(self):
        pass
        #self.wg.remove_design(self.gn)


    # -- get_absolute_references --
    def test_get_absolute_references_external_reference(self):
        n = Node("http://shortbol.org/v2#ChnR_PchnB/1",
                 model.identifiers.objects.dna,
                 name="ChnR_PchnB")
        res = self.canonicaliser._get_absolute_references(n)
        self.assertEqual(str(res),"http://sevahub.es/public/Canonical/ChnR_PchnB/1")

    def test_get_absolute_references_sequence(self):
        n = Node("http://shortbol.org/v2#test_get_absolute_references_sequence/1",
                 model.identifiers.objects.dna,
                 name="test_get_absolute_references_sequence",
                 **{model.identifiers.predicates.has_sequence:"aaaggaggtgt"}) 
        res = self.canonicaliser._get_absolute_references(n)
        self.assertEqual(str(res),"https://synbiohub.org/public/igem/BBa_K090505/1")

    def test_get_absolute_references_metadata(self):
        n = Node("http://shortbol.org/v2#test_get_absolute_references_metadata/1",
                 model.identifiers.objects.dna,
                 name="test_get_absolute_references_metadata",
                 **{rdflib.DCTERMS.description:["BBa_K1444016"]})
        res = self.canonicaliser._get_absolute_references(n)
        self.assertEqual(str(res),"https://synbiohub.org/public/igem/BBa_K1444016/1")
    
    def test_get_absolute_reference_truth(self):
        node = Node("https://shortbol.org/Unknown/1")
        vertex = Node("pveg")

        # Setup.
        for i in range(0,21):
            self.tg.synonyms.positive(node,vertex)

        res = self.canonicaliser._get_absolute_references(vertex)
        self.assertEqual(str(res),node.get_key())

        for i in range(0,21):
            self.tg.synonyms.negative(node,vertex)


    # -- get_potential_references --
    def test_get_potential_references_partial_sequence(self):
        # Case: The sequence is a partial match. 
        n = Node("http://shortbol.org/v2#test_get_absolute_references_sequence/1",
                 model.identifiers.objects.dna,
                 name="test_get_absolute_references_sequence",
                 **{model.identifiers.predicates.has_sequence:"caaggaggtgt"})
        feedback = self.canonicaliser._get_potential_references(n)
        self.fail("Partials dont work.")
        self.assertEqual(str(res),"https://synbiohub.org/public/igem/BBa_K090505/1")

    def test_get_potential_references_indirect_name_external(self):
        # Case: The URI name has a query that produces external references. 
        dg = self.wg.get_design("unknown_graph") 
        n = Node("http://shortbol.org/v2#Pveg/1",
                 model.identifiers.objects.promoter)
        feedback = self.canonicaliser._get_potential_references(n)
        for f,v in feedback.items():
            g = self.canonicaliser._miner.get_external(f)
            objs = list(g.triples((rdflib.URIRef(f),rdflib.RDF.type,None)))
            self.assertGreater(len(objs),0)
            self.assertEqual(v["score"],0)
            
    def test_get_potential_references_indirect_descriptor_truth(self):
        # Case: Metadata has a synonym of a reference in TG. 
        node = Node("https://shortbol.org/Unknown/1")
        vertex = Node("pveg")
        # Setup.
        for i in range(0,15):
            self.tg.synonyms.positive(node,vertex)
        feedback = self.canonicaliser._get_potential_references(vertex)
        self.assertEqual(feedback,{str(node) : {"score" : 75,"comment" : "pveg"}})
        for i in range(0,15):
            self.tg.synonyms.negative(node,vertex)


    # -- canonicalise --
    def test_canonicalise_get(self):
        fn = os.path.join("files","canonicalise_get.xml")
        gn = "test_canonicalise_get"
        try:
            self.wg.remove_design(gn)
        except Exception:
            pass

        convert(fn,self.wg.driver,gn)
        reps = self.canonicaliser.enhance(gn)
        for k,v in reps.items():
            self.assertIn(get_name(k),v)
            self.assertTrue(self.enhancer._miner.is_reference(v))

    def test_canonicalise_sequence(self):
        fn = os.path.join("files","canonicalise_sequence.xml")
        gn = "test_canonicalise_get"
        try:
            self.wg.remove_design(gn)
        except Exception:
            pass

        convert(fn,self.wg.driver,gn)
        reps = self.canonicaliser.enhance(gn)
        for k,v in reps.items():
            self.assertTrue(self.enhancer._miner.is_reference(v))

    def test_canonicalise_metadata(self):
        fn = os.path.join("files","canonicalise_metadata.xml")
        gn = "test_canonicalise_get"
        try:
            self.wg.remove_design(gn)
        except Exception:
            pass

        convert(fn,self.wg.driver,gn)
        reps = self.canonicaliser.enhance(gn)
        for k,v in reps.items():
            self.assertTrue(self.enhancer._miner.is_reference(v))

    def test_canonicalise_truth(self):
        fn = os.path.join("files","canonicalise_metadata.xml")
        gn = "test_design_truth"
        try:
            self.wg.remove_design(gn)
        except Exception:
            pass

        convert(fn,self.wg.driver,gn)
        reps = self.canonicaliser.enhance(gn)
        for k,v in reps.items():
            self.assertTrue(self.enhancer._miner.is_reference(v))

    def test_canonicalise_graph_automated(self):
        fn = os.path.join("files","canonicalise_get.xml")
        gn = "test_canonicalise_get"
        try:
            self.wg.remove_design(gn)
        except Exception:
            pass

        convert(fn,self.wg.driver,gn)
        dg = self.wg.get_design(gn)
        pre_pes = dg.get_physicalentity()
        self.canonicaliser.enhance(gn,mode="automated")
        post_pes = dg.get_physicalentity()
        diff = list(set(post_pes) - set(pre_pes))
        self.assertEqual(len(diff),len(pre_pes))
        for d in diff:
            response = requests.get(d)
            self.assertTrue(response.status_code == 200)
        dg.drop()

    def test_canonicalise_graph_semi_automated(self):
        fn = os.path.join("files","test_canonicalise_graph_semi_automated.xml")
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
        reps,fback = self.canonicaliser.enhance(gn,mode="semi_automated")
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


    # -- Post Rank -- 
    def test_post_rank_direct_standard_parts(self):
        fn = os.path.join("files","standard_parts.xml")
        gn = "test_post_rank"
        convert(fn,self.wg.driver,gn)
        dg = self.wg.get_design(gn)
        subject = "https://synbiohub.org/public/igem/my_region/1"
        potentials = {"https://synbiohub.org/public/igem/BBa_Q04121/1": {"score":0.72,"comment":""}}
        new_ps = self.canonicaliser._post_rank(subject,potentials,dg)
        self.assertEqual(new_ps,{"https://synbiohub.org/public/igem/BBa_Q04121/1": {"score":1.0,"comment":""}})
        dg.drop()

    def test_post_rank_direct_standard_module(self):
        fn = os.path.join("files","standard_module.xml")
        gn = "test_post_rank"
        convert(fn,self.wg.driver,gn)
        dg = self.wg.get_design(gn)
        parent = "https://synbiohub.org/public/igem/BBa_Q04121/1"
        subject = "https://synbiohub.org/public/igem/Elowitz_rbs/1"
        potentials = {"https://synbiohub.org/public/igem/BBa_B0034/1": 0.72}
        new_ps = self.canonicaliser._post_rank(subject,potentials,dg,parent=parent)
        self.assertEqual(new_ps,{"https://synbiohub.org/public/igem/BBa_B0034/1": 1.0})
        dg.drop()

def get_name(subject):
    split_subject = split(subject)
    if len(split_subject[-1]) == 1 and split_subject[-1].isdigit():
        return split_subject[-2]
    else:
        return split_subject[-1]

def split(uri):
    return re.split('#|\/|:', uri)