import sys
import os
import unittest
from rdflib import RDF
sys.path.insert(0, os.path.join(".."))
sys.path.insert(0, os.path.join("..",".."))
sys.path.insert(0, os.path.join("..","..",".."))
sys.path.insert(0, os.path.join("..","..","..",".."))
sys.path.insert(0, os.path.join("..","..","..","..",".."))
from world_graph import WorldGraph
from app.graph.utility.graph_objects.edge import Edge
from app.graph.utility.graph_objects.node import Node
from app.graph.utility.model.model import model

confidence = str(model.identifiers.external.confidence)

class TestTruthGraph(unittest.TestCase):
    
    @classmethod
    def setUpClass(self):
        self.wg = WorldGraph()
        self.tg = self.wg.truth

    @classmethod
    def tearDownClass(self):
        pass

    def setUp(self):
        pe = model.identifiers.objects.physical_entity
        i = model.identifiers.objects.interaction
        self.n1 = Node("PE1",pe)
        self.n2 = Node("I1",i)
        self.n3 = Node("PE2",pe)
        self.n4 = Node("I2",i)
        self.n5 = Node("I2_syn",i)
        self.n6 = Node("PE3",pe)
        self.n7 = Node("PE4",pe)
        self.n8 = Node(model.identifiers.objects.dna)

        self.edge = Edge(self.n1,self.n2,model.identifiers.predicates.repressor)
        self.edge2 = Edge(self.n3,self.n2,model.identifiers.predicates.repressed)
        self.edge3 = Edge(self.n3,self.n4,model.identifiers.predicates.activator)
        self.edge4 = Edge(self.n2,self.n4,model.identifiers.predicates.activator)
        self.edge5 = Edge(self.n4,self.n5,model.identifiers.external.synonym)

        self.edge6 = Edge(self.n1,self.n5,model.identifiers.predicates.repressor)
        self.edge7 = Edge(self.n3,self.n5,model.identifiers.predicates.repressed)
        self.edge8 = Edge(self.n5,self.n6,model.identifiers.predicates.activator)
        self.edge9 = Edge(self.n5,self.n7,model.identifiers.predicates.activator)

        self.edge9 = Edge(self.n7,self.n8,model.identifiers.external.type)
        
        self.edges = [self.edge,self.edge2,self.edge3,self.edge4,
                      self.edge5,self.edge6,self.edge7,self.edge8,self.edge9]
        for e in self.edges:
            self.tg.driver.remove_edge(e)
            self.tg.driver.remove_node(e.n)
            self.tg.driver.remove_node(e.v)
        self.tg.driver.submit()

    def tearDown(self):
        for e in self.edges:
            self.tg.driver.remove_edge(e)
            self.tg.driver.remove_node(e.n)
            self.tg.driver.remove_node(e.v)
        self.tg.driver.submit()


    def test_positive(self):
        self.tg.positive(self.edge)
        e = self.tg.get(self.edge)
        self.assertIsInstance(e,Edge)
        self.assertEqual(e,self.edge)
        conf = e[confidence]
        self.assertEqual(conf,self.tg._scm)
    
    def test_positive_increment(self):
        self.tg.positive(self.edge)
        e = self.tg.get(self.edge)
        self.assertIsInstance(e,Edge)
        self.assertEqual(e,self.edge)
        conf = e[confidence]
        self.assertEqual(conf,self.tg._scm)

        self.tg.positive(self.edge)
        e = self.tg.get(self.edge)
        self.assertIsInstance(e,Edge)
        self.assertEqual(e,self.edge)
        conf = e[confidence]
        self.assertEqual(conf,self.tg._scm*2)

        self.tg.positive(self.edge)
        e = self.tg.get(self.edge)
        self.assertIsInstance(e,Edge)
        self.assertEqual(e,self.edge)
        conf = e[confidence]
        self.assertEqual(conf,self.tg._scm*3)

    def test_positive_node_only(self):
        self.tg.positive(self.edge)
        e = self.tg.get(self.edge)
        self.assertIsInstance(e,Edge)
        self.assertEqual(e,self.edge)
        conf = e[confidence]
        self.assertEqual(conf,self.tg._scm)


        self.tg.positive(self.edge2)
        e = self.tg.get(self.edge2)
        self.assertIsInstance(e,Edge)
        self.assertEqual(e,self.edge2)
        conf = e[confidence]
        self.assertEqual(conf,self.tg._scm)

        self.tg.positive(self.edge3)
        e = self.tg.get(self.edge3)
        self.assertIsInstance(e,Edge)
        self.assertEqual(e,self.edge3)
        conf = e[confidence]
        self.assertEqual(conf,self.tg._scm)

        self.tg.positive(self.edge4)
        e = self.tg.get(self.edge4)
        self.assertIsInstance(e,Edge)
        self.assertEqual(e,self.edge4)
        conf = e[confidence]
        self.assertEqual(conf,self.tg._scm)
        

    def test_negative(self):
        self.tg.negative(self.edge)
        e = self.tg.get(self.edge)
        self.assertIsNone(e)

        conf_count = 0
        for i in range(0,5):
            self.tg.positive(self.edge)
            conf_count += self.tg._scm

        self.tg.negative(self.edge)
        conf_count -= self.tg._scm
        e = self.tg.get(self.edge)
        self.assertIsInstance(e,Edge)
        self.assertEqual(e,self.edge)
        conf = e[confidence]
        self.assertEqual(conf,conf_count)
    
    def test_negative_increment(self):        
        conf_count = 0
        for i in range(0,5):
            self.tg.positive(self.edge)
            conf_count += self.tg._scm

        self.tg.negative(self.edge)
        conf_count -= self.tg._scm
        e = self.tg.get(self.edge)
        self.assertIsInstance(e,Edge)
        self.assertEqual(e,self.edge)
        conf = e[confidence]
        self.assertEqual(conf,conf_count)

        self.tg.negative(self.edge)
        conf_count -= self.tg._scm
        e = self.tg.get(self.edge)
        self.assertIsInstance(e,Edge)
        self.assertEqual(e,self.edge)
        conf = e[confidence]
        self.assertEqual(conf,conf_count)

        self.tg.negative(self.edge)
        conf_count -= self.tg._scm
        e = self.tg.get(self.edge)
        self.assertIsInstance(e,Edge)
        self.assertEqual(e,self.edge)
        conf = e[confidence]
        self.assertEqual(conf,conf_count)
    
    def test_negative_node_only(self):        
        conf_count = 0
        for i in range(0,2):
            self.tg.positive(self.edge)
            self.tg.positive(self.edge2)
            self.tg.positive(self.edge3)
            self.tg.positive(self.edge4)
            conf_count += self.tg._scm
        conf_count -= self.tg._scm


        self.tg.negative(self.edge2)
        e = self.tg.get(self.edge2)
        self.assertIsInstance(e,Edge)
        self.assertEqual(e,self.edge2)
        conf = e[confidence]
        self.assertEqual(conf,conf_count)

        self.tg.negative(self.edge3)
        e = self.tg.get(self.edge3)
        self.assertIsInstance(e,Edge)
        self.assertEqual(e,self.edge3)
        conf = e[confidence]
        self.assertEqual(conf,conf_count)

        self.tg.negative(self.edge4)
        e = self.tg.get(self.edge4)
        self.assertIsInstance(e,Edge)
        self.assertEqual(e,self.edge4)
        conf = e[confidence]
        self.assertEqual(conf,conf_count)

    def test_lower_threshold(self):
        self.tg.positive(self.edge)
        self.tg.negative(self.edge)

        e = self.tg.get(self.edge4)
        self.assertIsNone(e)
        res = self.tg.driver.node_query([self.edge.n,self.edge.v])
        self.assertEqual(len(res),0)

    def test_upper_threshold_synonym(self):
        conf_count = 0
        while conf_count < self.tg._upper_threshold:
            self.tg.positive(self.edge5)
            conf_count += self.tg._scm
        self.assertEqual(self.tg.driver.edge_query(e_props={"graph_name" : self.tg.name}),[])
        res1 = self.tg.driver.node_query([self.edge5.n,self.edge5.v])
        res2 = self.tg.driver.node_query(self.edge5.v)
        res3 = self.tg.driver.node_query(self.edge5.v)
        self.assertEqual(res1,res2)
        self.assertEqual(res2,res3)

    def test_upper_threshold_synonym_nodes_with_edges(self):
        for i in range(0,1):
            self.tg.positive(self.edge)
            self.tg.positive(self.edge2)
            self.tg.positive(self.edge3)
            self.tg.positive(self.edge4)
            self.tg.positive(self.edge5)
            self.tg.positive(self.edge6)
            self.tg.positive(self.edge7)
            self.tg.positive(self.edge8)
            self.tg.positive(self.edge9)
        conf_count = 10

        pre_edges = (self.tg.driver.edge_query(n=self.edge5.n,e_props={"graph_name" : self.tg.name},directed=False) + 
                    self.tg.driver.edge_query(n=self.edge5.v,e_props={"graph_name" : self.tg.name},directed=False))

        while conf_count <= self.tg._upper_threshold:
            self.tg.positive(self.edge5)
            conf_count += self.tg._scm

        edges = self.tg.driver.edge_query(n=self.edge5.n,e_props={"graph_name" : self.tg.name},directed=False)
        merge_nodes = edges[0].n
        for e in pre_edges:
            if e.get_type() == str(model.identifiers.external.synonym):
                continue
            e.n = merge_nodes
            self.assertTrue(e in edges)

    def test_upper_threshold_type(self):
        conf_count = 0
        while conf_count < self.tg._upper_threshold:
            self.tg.positive(self.edge9)
            conf_count += self.tg._scm

        self.assertEqual(self.tg.driver.edge_query(e_props={"graph_name" : self.tg.name}),[])
        res1 = self.tg.driver.node_query([self.edge5.n,self.edge5.v])
        res2 = self.tg.driver.node_query(self.edge5.v)
        res3 = self.tg.driver.node_query(self.edge5.v)
        self.assertEqual(res1,res2)
        self.assertEqual(res2,res3)

