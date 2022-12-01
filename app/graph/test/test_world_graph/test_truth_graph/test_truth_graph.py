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
from app.graph.truth_graph.modules.abstract_module import AbstractModule
from app.graph.truth_graph.modules.synonym import SynonymModule
from app.graph.truth_graph.modules.interaction import InteractionModule
from app.graph.utility.graph_objects.edge import Edge
from app.graph.utility.graph_objects.node import Node
from app.graph.utility.model.model import model

curr_dir = os.path.dirname(os.path.realpath(__file__))
dfn = os.path.join(curr_dir,"..","..","files","nor_full.xml")
confidence = str(model.identifiers.external.confidence)

class TestTruthGraph(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.wg = WorldGraph()
        self.tg = self.wg.truth
        self.module = AbstractModule(self.tg)

    @classmethod
    def tearDownClass(self):
        pass

    def test_export_load(self):
        out_fn = "output.xml"
        pre_nodes = self.tg.nodes()
        pre_edges = self.tg.edges()

        self.tg.export(out_fn)

        self.wg.remove_design(self.tg.name)
        self.assertEqual(self.tg.nodes(),[])
        self.assertEqual(self.tg.edges(),[])

        self.tg.load(out_fn)

        post_nodes = self.tg.nodes()
        post_edges = self.tg.edges()

        ndiff = list(set(post_nodes) - set(pre_nodes))
        ediff = list(set(post_edges) - set(pre_edges))

        self.assertEqual(ndiff,[])
        self.assertEqual(ediff,[])

    class TestModule(unittest.TestCase):
        @classmethod
        def setUpClass(self):
            self.wg = WorldGraph()
            self.tg = self.wg.truth
            self.module = AbstractModule(self.tg)

        @classmethod
        def tearDownClass(self):
            pass

        def setUp(self):
            pe = model.identifiers.objects.physical_entity
            i = model.identifiers.objects.interaction
            self.props = {"graph_name" : self.tg.name}
            self.n1 = Node("PE1",pe,**self.props)
            self.n2 = Node("I1",i,**self.props)
            self.n3 = Node("PE2",pe,**self.props)
            self.n4 = Node("I2",i,**self.props)
            self.n5 = Node("I2_syn",i,**self.props)
            self.n6 = Node("PE3",pe,**self.props)
            self.n7 = Node("PE4",pe,**self.props)
            self.n8 = Node(model.identifiers.objects.dna,**self.props)

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


        def _edge_equal(self,actual,expected):
            expected.n.properties["graph_name"] = self.tg.name
            expected.n.graph_name = self.tg.name
            expected.v.properties["graph_name"] = self.tg.name
            expected.v.graph_name = self.tg.name
            expected.properties["graph_name"] = self.tg.name
            expected.graph_name = self.tg.name
            self.assertEqual(actual,expected)


        def test_positive(self):
            self.module.positive(self.edge)
            e = self.module.get(self.edge)
            self.assertIsInstance(e,Edge)
            self._edge_equal(e,self.edge)
            conf = e[confidence]
            self.assertEqual(conf,self.module._standard_modifier)
        
        def test_positive_increment(self):
            self.module.positive(self.edge)
            e = self.module.get(self.edge)
            self.assertIsInstance(e,Edge)
            self._edge_equal(e,self.edge)
            conf = e[confidence]
            self.assertEqual(conf,self.module._standard_modifier)

            self.module.positive(self.edge)
            e = self.module.get(self.edge)
            self.assertIsInstance(e,Edge)
            self._edge_equal(e,self.edge)
            conf = e[confidence]
            self.assertEqual(conf,self.module._standard_modifier*2)

            self.module.positive(self.edge)
            e = self.module.get(self.edge)
            self.assertIsInstance(e,Edge)
            self._edge_equal(e,self.edge)
            conf = e[confidence]
            self.assertEqual(conf,self.module._standard_modifier*3)

        def test_positive_node_only(self):
            self.module.positive(self.edge)
            e = self.module.get(self.edge)
            self.assertIsInstance(e,Edge)
            self._edge_equal(e,self.edge)
            conf = e[confidence]
            self.assertEqual(conf,self.module._standard_modifier)


            self.module.positive(self.edge2)
            e = self.module.get(self.edge2)
            self.assertIsInstance(e,Edge)
            self.assertEqual(e,self.edge2)
            conf = e[confidence]
            self.assertEqual(conf,self.module._standard_modifier)

            self.module.positive(self.edge3)
            e = self.module.get(self.edge3)
            self.assertIsInstance(e,Edge)
            self.assertEqual(e,self.edge3)
            conf = e[confidence]
            self.assertEqual(conf,self.module._standard_modifier)

            self.module.positive(self.edge4)
            e = self.module.get(self.edge4)
            self.assertIsInstance(e,Edge)
            self.assertEqual(e,self.edge4)
            conf = e[confidence]
            self.assertEqual(conf,self.module._standard_modifier)
            
        def test_negative(self):
            self.module.negative(self.edge)
            e = self.module.get(self.edge)
            self.assertIsNone(e)

            conf_count = 0
            for i in range(0,5):
                self.module.positive(self.edge)
                conf_count += self.module._standard_modifier

            self.module.negative(self.edge)
            conf_count -= self.module._standard_modifier
            e = self.module.get(self.edge)
            self.assertIsInstance(e,Edge)
            self._edge_equal(e,self.edge)
            conf = e[confidence]
            self.assertEqual(conf,conf_count)
        
        def test_negative_increment(self):        
            conf_count = 0
            for i in range(0,5):
                self.module.positive(self.edge)
                conf_count += self.module._standard_modifier

            self.module.negative(self.edge)
            conf_count -= self.module._standard_modifier
            e = self.module.get(self.edge)
            self.assertIsInstance(e,Edge)
            self._edge_equal(e,self.edge)
            conf = e[confidence]
            self.assertEqual(conf,conf_count)

            self.module.negative(self.edge)
            conf_count -= self.module._standard_modifier
            e = self.module.get(self.edge)
            self.assertIsInstance(e,Edge)
            self._edge_equal(e,self.edge)
            conf = e[confidence]
            self.assertEqual(conf,conf_count)

            self.module.negative(self.edge)
            conf_count -= self.module._standard_modifier
            e = self.module.get(self.edge)
            self.assertIsInstance(e,Edge)
            self._edge_equal(e,self.edge)
            conf = e[confidence]
            self.assertEqual(conf,conf_count)
        
        def test_negative_node_only(self):        
            conf_count = 0
            for i in range(0,2):
                self.module.positive(self.edge)
                self.module.positive(self.edge2)
                self.module.positive(self.edge3)
                self.module.positive(self.edge4)
                conf_count += self.module._standard_modifier
            conf_count -= self.module._standard_modifier


            self.module.negative(self.edge2)
            e = self.module.get(self.edge2)
            self.assertIsInstance(e,Edge)
            self.assertEqual(e,self.edge2)
            conf = e[confidence]
            self.assertEqual(conf,conf_count)

            self.module.negative(self.edge3)
            e = self.module.get(self.edge3)
            self.assertIsInstance(e,Edge)
            self.assertEqual(e,self.edge3)
            conf = e[confidence]
            self.assertEqual(conf,conf_count)

            self.module.negative(self.edge4)
            e = self.module.get(self.edge4)
            self.assertIsInstance(e,Edge)
            self.assertEqual(e,self.edge4)
            conf = e[confidence]
            self.assertEqual(conf,conf_count)

        def test_lower_threshold(self):
            d = self.wg.get_design("test_lower_threshold")
            n = self.edge.n.duplicate()
            v = self.edge.v.duplicate()
            n.remove(self.props)
            v.remove(self.props)
            edges = [(n,v,self.edge.get_type(),{})]
            d.add_edges(edges)
            self.module.positive(self.edge)
            self.module.negative(self.edge)

            e = self.module.get(self.edge)
            self.assertIsNone(e)
            res = d.edges(edges[0][0],edges[0][1],edges[0][2])
            self.assertEqual(len(res),1)
            self.assertEqual(self.edge,res[0])
            self.wg.remove_design("test_lower_threshold")

        def test_with_designs(self):
            self.wg.remove_design("test_with_designs")
            dg = self.wg.get_design("test_with_designs")
            edges = []
            for e in self.edges:
                n = e.n.duplicate()
                v = e.v.duplicate()
                n.remove(self.props)
                v.remove(self.props)
                edges.append((n,v,e.get_type(),{}))
            dg.add_edges(edges)
            pn = dg.nodes()
            self.module.positive(self.edge)
            self.module.negative(self.edge)
            pon = dg.nodes()
            self.assertCountEqual(pn,pon)

            res = self.module.get(self.edge)
            self.assertIsNone(res)

            self.wg.remove_design("test_with_designs")

    class TestSynonymModule(unittest.TestCase):
        @classmethod
        def setUpClass(self):
            self.wg = WorldGraph()
            self.tg = self.wg.truth
            self.module = SynonymModule(self.tg)

        @classmethod
        def tearDownClass(self):
            pass

        def setUp(self):
            pass

        def tearDown(self):
            pass

        def _edge_equal(self,actual,expected):
            expected.n.properties["graph_name"] = self.tg.name
            expected.n.graph_name = self.tg.name
            expected.v.properties["graph_name"] = self.tg.name
            expected.v.graph_name = self.tg.name
            expected.properties["graph_name"] = self.tg.name
            expected.graph_name = self.tg.name
            self.assertEqual(actual,expected)
        
        def _assert_edge_count_equal(self,actuals,expecteds):
            for e in expecteds:
                e.n.properties["graph_name"] = self.tg.name
                e.n.graph_name = self.tg.name
                e.v.properties["graph_name"] = self.tg.name
                e.v.graph_name = self.tg.name
                e.properties["graph_name"] = self.tg.name
                e.graph_name = self.tg.name

        def test_synonym_positive(self):
            node = Node("https://synbiohub.org/public/igem/BBa_K823003/1",model.identifiers.objects.physical_entity)
            vertex = Node("pveg")
            edge = Edge(node,vertex,model.identifiers.external.synonym)
            self.tg.remove_edge(edge)
            self.tg.driver.submit()
            

            self.module.positive(node,vertex)
            res = self.module.get(node,vertex,threshold=5)
            self.assertTrue(len(res) == 1)
            res = res[0]
            self._edge_equal(res,edge)
            self.assertEqual(res.confidence,5)
            self.module.positive(node,vertex)
            res = self.module.get(node,vertex,threshold=5)
            self.assertTrue(len(res) == 1)
            res = res[0]
            self._edge_equal(res,edge)
            self.assertEqual(res.confidence,10)

            node1 = Node("https://synbiohub.org/public/igem/pveg/1",name="pveg")
            vertex1 = Node("BBa_K823003")
            self.module.positive(node1,vertex1)
            res = self.module.get(node,vertex,threshold=5)
            self.assertTrue(len(res) == 1)
            res = res[0]
            self._edge_equal(res,edge)
            self.assertEqual(res.confidence,15)

            self.module.negative(node,vertex)
            self.module.negative(node,vertex)
            self.module.negative(node,vertex)

        def test_synonym_get(self):
            node = Node("https://synbiohub.org/public/igem/BBa_K823003/1",model.identifiers.objects.physical_entity)
            vertex = Node("pveg")
            edge = Edge(node,vertex,model.identifiers.external.synonym)
            self.tg.remove_edge(edge)
            self.tg.driver.submit()
            

            self.module.positive(node,vertex)
            res = self.module.get(node,vertex,threshold=5)
            self._edge_equal(res[0],edge)

            node1 = Node("https://synbiohub.org/public/igem/test/1",model.identifiers.objects.physical_entity)
            vertex1 = Node("tes")
            edge1 = Edge(node1,vertex1,model.identifiers.external.synonym)
            self.module.positive(node1,vertex1)

            self._assert_edge_count_equal(res,[edge,edge1])

        def test_synonym_negative(self):
            node = Node("https://synbiohub.org/public/igem/BBa_K823003/1",model.identifiers.objects.physical_entity)
            vertex = Node("pveg")
            edge = Edge(node,vertex,model.identifiers.external.synonym)
            self.tg.remove_edge(edge)
            self.tg.driver.submit()

            for i in range(0,2):
                self.module.positive(node,vertex)

            res = self.module.get(node,vertex,threshold=5)
            self.assertTrue(len(res),1)
            res = res[0]
            self.assertEqual(res.confidence,10)

            for i in range(0,2):
                self.module.negative(node,vertex)
            
            res = self.module.get(node,vertex,threshold=5)
            self.assertEqual(res,[])

            self.module.negative(node,vertex)
            res = self.module.get(node,vertex,threshold=5)
            self.assertEqual(res,[])

        def test_get_synonym_subject(self):
            node = Node("https://synbiohub.org/public/igem/BBa_K823003/1",model.identifiers.objects.physical_entity)
            vertex = Node("pveg")
            edge = Edge(node,vertex,model.identifiers.external.synonym)
            self.tg.remove_edge(edge)
            self.tg.driver.submit()

            for i in range(0,2):
                self.module.positive(node,vertex)

            res = self.module.get(synonym=vertex)
            self.assertTrue(len(res),1)
            res = res[0]
            self.assertEqual(res.confidence,10)

    class TestInteractionModule(unittest.TestCase):
        @classmethod
        def setUpClass(self):
            self.wg = WorldGraph()
            self.tg = self.wg.truth
            self.module = InteractionModule(self.tg)

        @classmethod
        def tearDownClass(self):
            pass

        def setUp(self):
            pass

        def tearDown(self):
            pass

        def _edge_equal(self,actual,expected):
            expected.n.properties["graph_name"] = self.tg.name
            expected.n.graph_name = self.tg.name
            expected.v.properties["graph_name"] = self.tg.name
            expected.v.graph_name = self.tg.name
            expected.properties["graph_name"] = self.tg.name
            expected.graph_name = self.tg.name
            self.assertEqual(actual,expected)
        
        def _assert_edge_count_equal(self,actuals,expecteds):
            for e in expecteds:
                e.n.properties["graph_name"] = self.tg.name
                e.n.graph_name = self.tg.name
                e.v.properties["graph_name"] = self.tg.name
                e.v.graph_name = self.tg.name
                e.properties["graph_name"] = self.tg.name
                e.graph_name = self.tg.name

        def test_interaction_positive(self):
            node = Node("https://synbiohub.org/public/igem/tetR/1",model.identifiers.objects.dna)
            vertex = Node("https://synbiohub.org/public/igem/repression/1",model.identifiers.objects.repression)
            edge = Edge(vertex,node,model.identifiers.predicates.repressor)
            self.tg.remove_edge(edge)
            self.tg.driver.submit()
            
            self.module.positive(edge)
            res = self.module.get(edge.n,edge.v,edge.get_type(),threshold=5)
            self.assertTrue(len(res) == 1)
            res = res[0]
            self._edge_equal(res,edge)
            self.assertEqual(res.confidence,5)
            self.module.positive(edge)
            res = self.module.get(edge.n,edge.v,edge.get_type(),threshold=5)
            self.assertTrue(len(res) == 1)
            res = res[0]
            self._edge_equal(res,edge)
            self.assertEqual(res.confidence,10)

            self.module.negative(edge)
            self.module.negative(edge)

        def test_interaction_get(self):
            node = Node("https://synbiohub.org/public/igem/tetR/1",model.identifiers.objects.dna)
            vertex = Node("https://synbiohub.org/public/igem/repression/1",model.identifiers.objects.repression)
            edge = Edge(vertex,node,model.identifiers.predicates.repressor)
            self.tg.remove_edge(edge)
            self.tg.driver.submit()
            
            self.module.positive(edge)
            res = self.module.get(edge.n,edge.v,edge.get_type(),threshold=5)
            self._edge_equal(res[0],edge)

        def test_synonym_negative(self):
            node = Node("https://synbiohub.org/public/igem/tetR/1",model.identifiers.objects.dna)
            vertex = Node("https://synbiohub.org/public/igem/repression/1",model.identifiers.objects.repression)
            edge = Edge(vertex,node,model.identifiers.predicates.repressor)
            self.tg.remove_edge(edge)
            self.tg.driver.submit()

            for i in range(0,2):
                self.module.positive(edge)

            res = self.module.get(edge.n,edge.v,edge.get_type(),threshold=5)
            self.assertTrue(len(res),1)
            res = res[0]
            self.assertEqual(res.confidence,10)

            for i in range(0,2):
                self.module.negative(edge)
            
            res = self.module.get(edge.n,edge.v,edge.get_type(),threshold=5)
            self.assertEqual(res,[])

            self.module.negative(edge)
            res = self.module.get(edge.n,edge.v,edge.get_type(),threshold=5)
            self.assertEqual(res,[])
