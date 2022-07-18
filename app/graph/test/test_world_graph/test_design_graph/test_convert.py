import sys
import os
import unittest

sys.path.insert(0, os.path.join(".."))
sys.path.insert(0, os.path.join("..",".."))
sys.path.insert(0, os.path.join("..","..",".."))
sys.path.insert(0, os.path.join("..","..","..",".."))
sys.path.insert(0, os.path.join("..","..","..","..",".."))
from world_graph import WorldGraph
from design_graph.converter.utility.graph import SBOLGraph
curr_dir = os.path.dirname(os.path.realpath(__file__))

class TestConvert(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_sbol(self):
        fn = os.path.join(curr_dir,"..","..","files","nor_full.xml")
        sbol_graph = SBOLGraph(fn)
        gn = "test_sbol"
        graph = WorldGraph()
        dg = graph.add_design(fn, gn)

        s_cds = [str(s) for s in sbol_graph.get_component_definitions()]
        pes = [p.get_key() for p in dg.get_physicalentity()]
        self.assertCountEqual(pes,s_cds)

        s_i = [str(s) for s in sbol_graph.get_interactions()]
        ints = [p.get_key() for p in dg.get_interaction()]
        self.assertCountEqual(ints,s_i)

        dg.drop()

    def test_gbk(self):
        fn = os.path.join(curr_dir,"..","..","files","nor_reporter.gb")
        gn = "test_gbk"
        graph = WorldGraph()
        dg = graph.add_design(fn, gn)
        pes = dg.get_physicalentity()
        root = pes.pop(0)
        for e in dg.get_haspart(root):
            self.assertEqual(root,e.n)
            self.assertIn(e.v,pes)
        dg.drop()

