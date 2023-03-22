import sys
import os
import unittest
from rdflib import Graph
sys.path.insert(0, os.path.join(".."))
sys.path.insert(0, os.path.join("..",".."))
sys.path.insert(0, os.path.join("..","..",".."))
sys.path.insert(0, os.path.join("..","..","..",".."))
from world_graph import WorldGraph
from converter.sbol_convert import convert
curr_dir = os.path.dirname(os.path.realpath(__file__))
fn = os.path.join(curr_dir,"..","..","test","files","nor_full.xml")

class TestWorldGraph(unittest.TestCase):
    
    @classmethod
    def setUpClass(self):
        self.gn = "test_wg"
        self.wg = WorldGraph()
        convert(fn,self.wg.driver,self.gn)
        self.dg = self.wg.get_design(self.gn)

    @classmethod
    def tearDownClass(self):
        self.wg.remove_design(self.gn)

    def test_add(self):
        self.assertEqual(self.dg.name,[self.gn])
        nodes = self.dg.nodes()
        edges = self.dg.edges()
        self.assertTrue(len(nodes) > 0)
        self.assertTrue(len(edges) > 0)
        for n in nodes:
            self.assertIn(self.gn,n.graph_name)
        for e in edges:
            self.assertIn(self.gn,e.n.graph_name)
            self.assertIn(self.gn,e.v.graph_name)
            self.assertIn(self.gn,e.graph_name)

    def test_get(self):
        dg = self.wg.get_design(self.gn)
        self.assertEqual(dg.name,[self.gn])
        nodes = dg.nodes()
        edges = dg.edges()
        self.assertTrue(len(nodes) > 0)
        self.assertTrue(len(edges) > 0)
        for n in nodes:
            self.assertIn(self.gn,n.graph_name)
        for e in edges:
            self.assertIn(self.gn,e.n.graph_name)
            self.assertIn(self.gn,e.v.graph_name)
            self.assertIn(self.gn,e.graph_name)

    def test_get_multiple(self):
        gn2 = "test_wg1"
        nodes = self.dg.nodes()
        self.wg.remove_design(gn2)

        dg = self.wg.get_design([self.gn,gn2],predicate="ALL")
        self.assertEqual(dg.nodes(),[])
        dg = self.wg.get_design([self.gn,gn2],predicate="ANY")
        for n in dg.nodes():
            self.assertIn(n,nodes)
        dg = self.wg.get_design([self.gn,gn2],predicate="SINGLE")
        for n in dg.nodes():
            self.assertIn(n,nodes)



        convert(fn,self.wg.driver,gn2)
        dg = self.wg.get_design([self.gn,gn2],predicate="ALL")
        for n in dg.nodes():
            self.assertIn(n,nodes)
        dg = self.wg.get_design([self.gn,gn2],predicate="ANY")
        for n in dg.nodes():
            self.assertIn(n,nodes)
        dg = self.wg.get_design([self.gn,gn2],predicate="SINGLE")
        self.assertEqual(dg.nodes(),[])

        gn3 = "test_wg2"
        fn1 = os.path.join(curr_dir,"..","..","test","files","nor_full.xml")
        convert(fn1,self.wg.driver,gn3)
        
        dg = self.wg.get_design([self.gn,gn2],predicate="ALL")
        for n in dg.nodes():
            self.assertIn(n,nodes)
        dg = self.wg.get_design([self.gn,gn2],predicate="ANY")
        for n in dg.nodes():
            self.assertIn(n,nodes)
        dg = self.wg.get_design([self.gn,gn2],predicate="SINGLE")
        self.assertEqual(dg.nodes(),[])

        self.wg.remove_design(gn2)
        self.wg.remove_design(gn3)

    def test_get_design_names(self):
        d_names = self.wg.get_design_names()
        self.assertIn(self.gn,d_names)

    def test_remove_design(self):
        self.wg.remove_design(self.gn)
        dg = self.wg.get_design(self.gn)
        self.assertEqual(dg.nodes(),[])
        self.assertEqual(dg.edges(),[])
        convert(fn,self.wg.driver,self.gn)

    def test_get_multiple_ALL(self):
        gn1 = "test_wg_get_all1"
        gn2 = "test_wg_get_all2"
        gn3 = "test_wg_get_all3"

        fn1 = os.path.join(curr_dir,"..","..","test","files","0xC7.xml")
        fn2 = os.path.join(curr_dir,"..","..","test","files","0x87.xml")
        fn3 = os.path.join(curr_dir,"..","..","test","files","0x3B.xml")

        convert(fn1,self.wg.driver,gn1)
        convert(fn2,self.wg.driver,gn2)
        convert(fn3,self.wg.driver,gn3)
        dg1 = self.wg.get_design([gn1])
        dg2 = self.wg.get_design([gn2])
        dg3 = self.wg.get_design([gn3])
        nodes1 = dg1.nodes()
        nodes2 = dg2.nodes()
        nodes3 = dg3.nodes()
        edges1 = dg1.edges()
        edges2 = dg2.edges()
        edges3 = dg3.edges()
        dg = self.wg.get_design([gn1,gn2,gn3],predicate="ALL")
        for node in dg.nodes():
            self.assertTrue(node in nodes1 and node in nodes2 and node in nodes3)
        for edge in dg.edges():
            self.assertTrue(edge in edges1 and edge in edges2 and edge in edges3)

        self.wg.remove_design(gn1)
        self.wg.remove_design(gn2)
        self.wg.remove_design(gn3)

    def test_get_multiple_ANY(self):
        gn1 = "test_wg_get_all1"
        gn2 = "test_wg_get_all2"
        gn3 = "test_wg_get_all3"

        fn1 = os.path.join(curr_dir,"..","..","test","files","0xC7.xml")
        fn2 = os.path.join(curr_dir,"..","..","test","files","0x87.xml")
        fn3 = os.path.join(curr_dir,"..","..","test","files","0x3B.xml")

        convert(fn1,self.wg.driver,gn1)
        convert(fn2,self.wg.driver,gn2)
        convert(fn3,self.wg.driver,gn3)
        dg1 = self.wg.get_design([gn1])
        dg2 = self.wg.get_design([gn2])
        dg3 = self.wg.get_design([gn3])
        nodes1 = dg1.nodes()
        nodes2 = dg2.nodes()
        nodes3 = dg3.nodes()
        edges1 = dg1.edges()
        edges2 = dg2.edges()
        edges3 = dg3.edges()
        dg = self.wg.get_design([gn1,gn2,gn3],predicate="ANY")
        for node in dg.nodes():
            self.assertTrue(node in nodes1 or node in nodes2 or node in nodes3)
        for edge in dg.edges():
            self.assertTrue(edge in edges1 or edge in edges2 or edge in edges3)

        self.wg.remove_design(gn1)
        self.wg.remove_design(gn2)
        self.wg.remove_design(gn3)

    def test_get_multiple_SINGLE(self):
        gn1 = "test_wg_get_all1"
        gn2 = "test_wg_get_all2"
        gn3 = "test_wg_get_all3"

        fn1 = os.path.join(curr_dir,"..","..","test","files","0xC7.xml")
        fn2 = os.path.join(curr_dir,"..","..","test","files","0x87.xml")
        fn3 = os.path.join(curr_dir,"..","..","test","files","0x3B.xml")

        convert(fn1,self.wg.driver,gn1)
        convert(fn2,self.wg.driver,gn2)
        convert(fn3,self.wg.driver,gn3)
        dg1 = self.wg.get_design([gn1])
        dg2 = self.wg.get_design([gn2])
        dg3 = self.wg.get_design([gn3])
        nodes1 = dg1.nodes()
        nodes2 = dg2.nodes()
        nodes3 = dg3.nodes()
        edges1 = dg1.edges()
        edges2 = dg2.edges()
        edges3 = dg3.edges()
        dg = self.wg.get_design([gn1,gn2,gn3],predicate="SINGLE")
        for node in dg.nodes():
            self.assertTrue([node in nodes1,node in nodes2,node in nodes3].count(True) == 1)
        for edge in dg.edges():
            self.assertTrue([edge in edges1,edge in edges2 or edge in edges3].count(True) == 1)
        self.wg.remove_design(gn1)
        self.wg.remove_design(gn2)
        self.wg.remove_design(gn3)