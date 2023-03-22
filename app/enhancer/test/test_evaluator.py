import sys
import os
import unittest
import re
sys.path.insert(0, os.path.join(".."))
sys.path.insert(0, os.path.join("..",".."))
sys.path.insert(0, os.path.join("..","..",".."))
sys.path.insert(0, os.path.join("..","..","..",".."))
from app.graph.world_graph import WorldGraph
from app.graph.utility.graph_objects.node import Node
from app.enhancer.enhancer import Enhancer
from converter.sbol_convert import convert
from app.enhancer.evaluator.completeness.sequence import SequenceEvaluator
from app.enhancer.evaluator.standard.referential import ReferentialEvaluator
from app.enhancer.evaluator.standard.derived_type import TypeEvaluator
from app.enhancer.evaluator.completeness.interaction import ExpectedInteractionEvaluator
from app.enhancer.evaluator.completeness.interaction import part_int_map
from app.enhancer.evaluator.completeness.interaction import PathwayEvaluator
from app.enhancer.evaluator.completeness.hierarchy import HierarchyEvaluator
curr_dir = os.path.dirname(os.path.realpath(__file__))


class TestEvaluator(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.wg = WorldGraph()
        self.enhancer = Enhancer(self.wg)
        self.evaluator = self.enhancer._evaluator
        fn = os.path.join("files","nor_full.xml")
        gn = "test_evaluator"
        #self.wg.remove_design(gn)
        #convert(fn,self.wg.driver,gn)
        self.graph = self.wg.get_design(gn)

    @classmethod
    def tearDownClass(self):
        self.graph.drop()
    
    def test_evaluator_none(self):
        gn = "test_evaluator"
        self.wg.remove_design(gn)
        feedback = self.evaluator.evaluate(gn)
        def traverse(d):
            if "score" not in d:
                return 
            score = d["score"]
            self.assertEqual(score,0)
            for k, v in d.items():
                if isinstance(v, dict):
                    traverse(v)
        traverse(feedback)

    def test_sequence_evaluator(self):
        dna = self.graph.get_dna()
        se = SequenceEvaluator(self.wg,self.enhancer._miner)
        feedback = se.evaluate(self.graph)
        p = []
        n_p = []
        for d in dna:
            if not hasattr(d,"hasSequence"):
                self.assertIn(d.get_key(),feedback["comments"])
                n_p.append(d)
            else:
                p.append(d)
        self.assertEqual(feedback["score"],int(len(p) / len(dna) * 100))

    def test_referential_evaluator(self):
        dna = self.graph.get_dna()
        se = ReferentialEvaluator(self.wg,self.enhancer._miner)
        feedback = se.evaluate(self.graph)
        fails = len(feedback["comments"])
        passes = len(dna) - fails
        self.assertEqual(feedback["score"],passes/len(dna) * 100)

    def test_derived_type_evaluator(self):
        dna = [e for e in self.graph.get_dna() if self.graph.get_children(e) == []]
        se = TypeEvaluator(self.wg,self.enhancer._miner)
        feedback = se.evaluate(self.graph)
        fails = len(feedback["comments"])
        passes = len(dna) - fails
        self.assertEqual(feedback["score"],int(passes/len(dna) * 100))

    def test_expected_interaction_evaluator(self):
        fn = os.path.join("files","test_expected_interaction_evaluator.xml")
        gn = "test_evaluator"
        self.wg.remove_design(gn)
        convert(fn,self.wg.driver,gn)
        graph = self.wg.get_design(gn)
        se = ExpectedInteractionEvaluator(self.wg,self.enhancer._miner)
        feedback = se.evaluate(graph)
        for k,v in feedback["comments"].items():
            node = graph.nodes(k)[0]
            ints = [e.n.get_type() for e in graph.get_interactions(k)]
            self.assertTrue(len(ints) == 0 or list(set(ints) & set(part_int_map[node.get_type()])) == [])

    def test_pathway_evaluator_disconnected(self):
        se = PathwayEvaluator(self.wg,self.enhancer._miner)
        fn = os.path.join("files","0x3B.xml")
        gn = "test_pathway_evaluator_disconnected"
        self.wg.remove_design(gn)
        convert(fn,self.wg.driver,gn)
        graph = self.wg.get_design(gn)
        n = Node("https://synbiohub.programmingbiology.org/public/Cello_VPRGeneration_Paper/v2_circuit_0x3B_2_A1_AmtR_module/Ara_AraC_protein_pBAD_activation/1")
        graph.remove_node(n)
        se = PathwayEvaluator(self.wg,self.enhancer._miner)
        feedback = se.evaluate(graph)
        self.assertEqual(feedback["score"],0)

    def test_pathway_evaluator_no_interactions(self):
        se = PathwayEvaluator(self.wg,self.enhancer._miner)
        fn = os.path.join("files","canonicalise_get.xml")
        gn = "test_pathway_evaluator_no_interactions"
        self.wg.remove_design(gn)
        convert(fn,self.wg.driver,gn)
        graph = self.wg.get_design(gn)
        se = PathwayEvaluator(self.wg,self.enhancer._miner)
        feedback = se.evaluate(graph)
        self.assertEqual(feedback["score"],0)

    def test_pathway_evaluator_no_io(self):
        se = PathwayEvaluator(self.wg,self.enhancer._miner)
        fn = os.path.join("files","cycle_i_graph.xml")
        gn = "test_pathway_evaluator_no_io"
        self.wg.remove_design(gn)
        convert(fn,self.wg.driver,gn)
        graph = self.wg.get_design(gn)
        se = PathwayEvaluator(self.wg,self.enhancer._miner)
        feedback = se.evaluate(graph)
        self.assertEqual(feedback["score"],50)

    def test_pathway_evaluator_no_i(self):
        se = PathwayEvaluator(self.wg,self.enhancer._miner)
        fn = os.path.join("files","test_pathway_evaluator_no_i.xml")
        gn = "test_pathway_evaluator_no_i"
        self.wg.remove_design(gn)
        convert(fn,self.wg.driver,gn)
        graph = self.wg.get_design(gn)
        se = PathwayEvaluator(self.wg,self.enhancer._miner)
        feedback = se.evaluate(graph)
        self.assertTrue(len(feedback["comments"]) == 1)
        self.assertEqual(feedback["score"],100)

    def test_pathway_evaluator_no_i_no_path(self):
        se = PathwayEvaluator(self.wg,self.enhancer._miner)
        fn = os.path.join("files","test_pathway_evaluator_no_i_no_path.xml")
        gn = "test_pathway_evaluator_no_i_no_path"
        self.wg.remove_design(gn)
        convert(fn,self.wg.driver,gn)
        graph = self.wg.get_design(gn)
        se = PathwayEvaluator(self.wg,self.enhancer._miner)
        feedback = se.evaluate(graph)
        self.assertEqual(feedback["score"],0)
        graph.drop()

    def test_pathway_evaluator_no_o(self):
        se = PathwayEvaluator(self.wg,self.enhancer._miner)
        fn = os.path.join("files","test_pathway_evaluator_no_o.xml")
        gn = "test_pathway_evaluator_no_o"
        self.wg.remove_design(gn)
        convert(fn,self.wg.driver,gn)
        graph = self.wg.get_design(gn)
        se = PathwayEvaluator(self.wg,self.enhancer._miner)
        feedback = se.evaluate(graph)
        self.assertTrue(len(feedback["comments"]) == 1)
        self.assertEqual(feedback["score"],100)

    def test_pathway_evaluator_no_path(self):
        se = PathwayEvaluator(self.wg,self.enhancer._miner)
        fn = os.path.join("files","test_pathway_evaluator_no_affectors_present.xml")
        gn = "test_pathway_evaluator_no_affectors_present"
        self.wg.remove_design(gn)
        convert(fn,self.wg.driver,gn)
        graph = self.wg.get_design(gn)
        se = PathwayEvaluator(self.wg,self.enhancer._miner)
        feedback = se.evaluate(graph)
        self.assertEqual(feedback["score"],0)
        comments = feedback["comments"]
        self.assertCountEqual(list(comments.keys()),["http://shortbol.org/v2#sm1/1","http://shortbol.org/v2#sm2/1","http://shortbol.org/v2#sm3/1"])

    def test_hierarchy_single_parent_no_shared(self):
        fn = os.path.join("files","single_parent_no_shared.xml")
        gn = "test_hierarchy_single_parent_no_shared"
        self.wg.remove_design(gn)
        convert(fn,self.wg.driver,gn)
        graph = self.wg.get_design(gn)
        se = HierarchyEvaluator(self.wg,self.enhancer._miner)
        feedback = se.evaluate(graph)
        self.assertEqual(feedback["score"],0)
        graph.drop()

    def test_hierarchy_single_parent_intermediate_shared(self):
        fn = os.path.join("files","single_parent_intermediate_shared.xml")
        gn = "test_hierarchy_single_parent_intermediate_shared"
        self.wg.remove_design(gn)
        convert(fn,self.wg.driver,gn)
        graph = self.wg.get_design(gn)
        se = HierarchyEvaluator(self.wg,self.enhancer._miner)
        feedback = se.evaluate(graph)
        self.assertEqual(feedback["score"],0)

    def test_hierarchy_single_parent_intermediate_parent_share(self):
        fn = os.path.join("files","single_parent_intermediate_parent_share.xml")
        gn = "test_hierarchy_single_parent_intermediate_parent_share"
        self.wg.remove_design(gn)
        convert(fn,self.wg.driver,gn)
        graph = self.wg.get_design(gn)
        se = HierarchyEvaluator(self.wg,self.enhancer._miner)
        feedback = se.evaluate(graph)
        self.assertEqual(feedback["score"],0)

    def test_hierarchy_single_parent_intermediate_cyclic(self):
        fn = os.path.join("files","single_parent_intermediate_cyclic.xml")
        gn = "test_hierarchy_single_parent_intermediate_cyclic"
        self.wg.remove_design(gn)
        convert(fn,self.wg.driver,gn)
        graph = self.wg.get_design(gn)
        se = HierarchyEvaluator(self.wg,self.enhancer._miner)
        feedback = se.evaluate(graph)
        self.assertEqual(feedback["comments"],{Node("http://shortbol.org/v2#intermediate_1/1"): 
        "http://shortbol.org/v2#intermediate_1/1 and http://shortbol.org/v2#intermediate_3/1 makes the hierarchy circular."})
        self.assertEqual(feedback["score"],0)

    def test_hierarchy_circular(self):
        fn = os.path.join("files","circular.xml")
        gn = "test_hierarchy_circular"
        self.wg.remove_design(gn)
        convert(fn,self.wg.driver,gn)
        graph = self.wg.get_design(gn)
        se = HierarchyEvaluator(self.wg,self.enhancer._miner)
        feedback = se.evaluate(graph)
        self.assertEqual(feedback["comments"],{'Design': 'Circular Hierarchy'})
        self.assertEqual(feedback["score"],0)

    def test_hierarchy_multiple_parent_shared_parts(self):
        fn = os.path.join("files","multiple_parent_shared_parts.xml")
        gn = "test_hierarchy_multiple_parent_shared_parts"
        self.wg.remove_design(gn)
        convert(fn,self.wg.driver,gn)
        graph = self.wg.get_design(gn)
        se = HierarchyEvaluator(self.wg,self.enhancer._miner)
        feedback = se.evaluate(graph)
        self.assertEqual(feedback["score"],0)

    def test_hierarchy_multiple_parent_shared_intermediate(self):
        fn = os.path.join("files","multiple_parent_shared_intermediate.xml")
        gn = "test_hierarchy_multiple_parent_shared_intermediate"
        self.wg.remove_design(gn)
        convert(fn,self.wg.driver,gn)
        graph = self.wg.get_design(gn)
        se = HierarchyEvaluator(self.wg,self.enhancer._miner)
        feedback = se.evaluate(graph)
        self.assertEqual(feedback["score"],0)

    def test_hierarchy_multiple_parent_disconnected(self):
        fn = os.path.join("files","multiple_parent_disconnected.xml")
        gn = "test_hierarchy_multiple_parent_disconnected"
        self.wg.remove_design(gn)
        convert(fn,self.wg.driver,gn)
        graph = self.wg.get_design(gn)
        se = HierarchyEvaluator(self.wg,self.enhancer._miner)
        feedback = se.evaluate(graph)
        self.assertEqual(feedback["score"],0)

    def test_hierarchy_parent_leafs_only(self):
        fn = os.path.join("files","parent_leafs_only.xml")
        gn = "test_hierarchy_parent_leafs_only"
        self.wg.remove_design(gn)
        convert(fn,self.wg.driver,gn)
        graph = self.wg.get_design(gn)
        se = HierarchyEvaluator(self.wg,self.enhancer._miner)
        feedback = se.evaluate(graph)
        self.assertEqual(feedback["score"],0)

    def test_hierarchy_single_parent_isolated_node(self):
        fn = os.path.join("files","single_parent_isolated_node.xml")
        gn = "test_hierarchy_single_parent_isolated_node"
        self.wg.remove_design(gn)
        convert(fn,self.wg.driver,gn)
        graph = self.wg.get_design(gn)
        se = HierarchyEvaluator(self.wg,self.enhancer._miner)
        feedback = se.evaluate(graph)
        self.assertEqual(feedback["score"],0)
        
def get_name(subject):
    split_subject = split(subject)
    if len(split_subject[-1]) == 1 and split_subject[-1].isdigit():
        return split_subject[-2]
    else:
        return split_subject[-1]

def split(uri):
    return re.split('#|\/|:', uri)