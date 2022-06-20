import sys
import os
import unittest

sys.path.insert(0, os.path.join(".."))
sys.path.insert(0, os.path.join("..",".."))
sys.path.insert(0, os.path.join("..","..",".."))
sys.path.insert(0, os.path.join("..","..","..",".."))
from neo4j_interface.interface import Neo4jInterface
curr_dir = os.path.dirname(os.path.realpath(__file__))

class TestInterface(unittest.TestCase):
    def setUp(self):
        self.interface = Neo4jInterface()

    def tearDown(self):
        pass

    def test_node(self):
        gn = "test_graph_convert"
        gn2 = "test_graph_convert2"
        self.interface.remove_graph(gn)
        in_nodes = [("key","type")]
        for k,t in in_nodes:
            res = self.interface.add_node(k,graph_name=[gn])
            self.interface.submit()
            res_q = self.interface.node_query(k)
            self.assertEqual(res,res_q[0])
            self.interface.add_node(k,graph_name=[gn2])
            self.interface.submit()
            gn_res = self.interface.node_query(graph_name=[gn])
            self.assertEqual(res,gn_res[0])
        self.interface.remove_graph(gn)
        self.assertEqual(self.interface.node_query(graph_name=gn),[])
        self.assertEqual(self.interface.node_query(graph_name=gn2)[0].get_key(),in_nodes[0][0])
        self.interface.remove_graph(gn2)

    def test_edge(self):
        gn = "test_graph_convert"
        gn2 = "test_graph_convert2"
        self.interface.remove_graph(gn)
        in_edges = [("key","key1","e_type")]
        for n,v,e in in_edges:
            nodey = self.interface.add_node(n,graph_name=[gn])
            self.interface.add_node(v,graph_name=[gn])
            res = self.interface.add_edge(n,v,e,graph_name = [gn])
            self.interface.submit()
            res_q = self.interface.edge_query(n,v,e)
            self.assertEqual(res,res_q[0])
            self.interface.add_node(n,graph_name=[gn2])
            self.interface.add_node(v,graph_name=[gn2])
            self.interface.add_edge(n,v,e,graph_name = [gn2])
            self.interface.submit()
            gn_res = self.interface.edge_query(e_props={"graph_name":[gn2]})
            self.assertEqual(res,gn_res[0])

        self.interface.remove_graph(gn)
        res = self.interface.edge_query(e_props={"graph_name":[gn]})
        self.assertEqual(res,[])
        self.assertEqual(self.interface.edge_query(e_props={"graph_name":[gn2]})[0].get_type(),in_edges[0][2])
        self.interface.remove_graph(gn2)