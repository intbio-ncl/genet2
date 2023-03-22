import sys
import os
import unittest

sys.path.insert(0, os.path.join(".."))
sys.path.insert(0, os.path.join("..",".."))
sys.path.insert(0, os.path.join("..","..",".."))
sys.path.insert(0, os.path.join("..","..","..",".."))
from neo4j_interface.interface import Neo4jInterface
from app.graph.utility.graph_objects.node import Node
from app.graph.utility.graph_objects.edge import Edge
from app.graph.utility.model.model import model
curr_dir = os.path.dirname(os.path.realpath(__file__))
gn = "TestInterface"
gn2 = "TestInterface2"
ids = model.identifiers

class TestInterface(unittest.TestCase):
    def setUp(self):
        self.reserved_names = ["truth_graph"]
        self.interface = Neo4jInterface(reserved_names=self.reserved_names)
        self.interface.remove_graph(gn)
        self.interface.remove_graph(gn2)
        self.interface.remove_graph(self.reserved_names)
    def tearDown(self):
        return
        self.interface.remove_graph(gn)
        self.interface.remove_graph(gn2)
        self.interface.remove_graph(self.reserved_names)


    def test_add_nodes(self):
        # Add Non-Reserved.
        node = Node("node1",ids.objects.physical_entity)
        self.interface.add_node(node,graph_name=[gn])
        pre_n = list(self.interface.nodes)
        self.interface.submit()
        post_n = list(self.interface.nodes)
        n_diff = list(set(post_n) - set(pre_n))
        self.assertEqual(len(n_diff),1)
        self.assertEqual(node,n_diff[0])

        # Add Existing Non-Reserved
        self.interface.add_node(node.get_key(),node.get_type(),graph_name=[gn])
        pre_n = list(self.interface.nodes)
        self.interface.submit()
        post_n = list(self.interface.nodes)
        n_diff = list(set(post_n) - set(pre_n))
        self.assertEqual(len(n_diff),0)

        # Add Existing Non-Reserved different graph name
        self.interface.add_node(node.get_key(),node.get_type(),graph_name=[gn2])
        pre_n = list(self.interface.nodes)
        self.interface.submit()
        post_n = list(self.interface.nodes)
        n_diff = list(set(post_n) - set(pre_n))
        self.assertEqual(len(n_diff),0)

        # Add Reserved with non-reserved present.
        res_node = Node(node.get_key(),node.get_type(),graph_name=self.reserved_names)
        res_node = self.interface.add_node(res_node)
        pre_n = list(self.interface.nodes)
        self.interface.submit()
        post_n = list(self.interface.nodes)
        n_diff = list(set(post_n) - set(pre_n))
        self.assertEqual(len(n_diff),1)
        self.assertCountEqual(n_diff,[res_node])
        self.assertCountEqual([a for tup in n_diff for a in tup["graph_name"]],self.reserved_names)

        # Add reserved with non-reserved not present.
        res_node = Node("node2",ids.objects.physical_entity,graph_name=self.reserved_names)
        res_node = self.interface.add_node(res_node)
        pre_n = list(self.interface.nodes)
        self.interface.submit()
        post_n = list(self.interface.nodes)
        n_diff = list(set(post_n) - set(pre_n))
        self.assertEqual(len(n_diff),1)
        self.assertCountEqual(n_diff,[res_node])

        # Add Non-reserved with reserved present.
        res_node = Node("node2",ids.objects.physical_entity,graph_name=[gn])
        res_node = self.interface.add_node(res_node)
        pre_n = list(self.interface.nodes)
        self.interface.submit()
        post_n = list(self.interface.nodes)
        n_diff = list(set(post_n) - set(pre_n))
        self.assertEqual(len(n_diff),1)

        # Add reserved with reserved and non-reserved present.
        res_node = Node(node.get_key(),node.get_type(),graph_name=self.reserved_names)
        res_node = self.interface.add_node(res_node)
        pre_n = list(self.interface.nodes)
        self.interface.submit()
        post_n = list(self.interface.nodes)
        n_diff = list(set(post_n) - set(pre_n))
        self.assertEqual(len(n_diff),0)


    def test_add_edges(self):
        node = Node("node",ids.objects.physical_entity,graph_name=[gn])
        node1 = Node("node1",ids.objects.physical_entity,graph_name=[gn])
        node2 = Node("node2",ids.objects.physical_entity,graph_name=[gn])
        node3 = Node("node3",ids.objects.physical_entity,graph_name=[gn])

        rnode = Node("node",ids.objects.physical_entity,graph_name=self.reserved_names)
        rnode1 = Node("node1",ids.objects.physical_entity,graph_name=self.reserved_names)
        rnode2 = Node("node2",ids.objects.physical_entity,graph_name=self.reserved_names)
        rnode3 = Node("node3",ids.objects.physical_entity,graph_name=self.reserved_names)
        # Add Non-Reserved.
        edge = self.interface.add_edge(n=node,v=node1,e=ids.predicates.has_part,graph_name=[gn])
        
        pre_n = list(self.interface.nodes)
        pre_e = list(self.interface.edges)
        self.interface.submit()
        post_n = list(self.interface.nodes)
        post_e = list(self.interface.edges)
        n_diff = list(set(post_n) - set(pre_n))
        e_diff = list(set(post_e) - set(pre_e))

        self.assertEqual(len(n_diff),2)
        self.assertEqual(len(e_diff),1)
        self.assertCountEqual([node,node1],n_diff)
        self.assertCountEqual([edge],e_diff)
        # Add Non-Reserved - Present
        self.interface.add_edge(n=node,v=node1,e=ids.predicates.has_part,graph_name=[gn])
        pre_n = list(self.interface.nodes)
        pre_e = list(self.interface.edges)
        self.interface.submit()
        post_n = list(self.interface.nodes)
        post_e = list(self.interface.edges)
        n_diff = list(set(post_n) - set(pre_n))
        e_diff = list(set(post_e) - set(pre_e))

        self.assertEqual(len(n_diff),0)
        self.assertEqual(len(e_diff),0)

        # Add Non-Reserved - Not Present
        edge = self.interface.add_edge(n=node,v=node2,e=ids.predicates.has_part,graph_name=[gn])

        pre_n = list(self.interface.nodes)
        pre_e = list(self.interface.edges)
        self.interface.submit()
        post_n = list(self.interface.nodes)
        post_e = list(self.interface.edges)
        n_diff = list(set(post_n) - set(pre_n))
        e_diff = list(set(post_e) - set(pre_e))

        self.assertEqual(len(n_diff),1)
        self.assertEqual(len(e_diff),1)
        self.assertCountEqual([node2],n_diff)
        self.assertCountEqual([edge],e_diff)

        # Add Reserved - Not Present
        edge = self.interface.add_edge(n=rnode,v=rnode1,e=ids.predicates.has_part,graph_name=self.reserved_names)

        pre_n = list(self.interface.nodes)
        pre_e = list(self.interface.edges)
        self.interface.submit()
        post_n = list(self.interface.nodes)
        post_e = list(self.interface.edges)
        n_diff = list(set(post_n) - set(pre_n))
        e_diff = list(set(post_e) - set(pre_e))

        self.assertEqual(len(n_diff),2)
        self.assertEqual(len(e_diff),1)
        self.assertCountEqual([edge.n,edge.v],n_diff)
        self.assertCountEqual([edge],e_diff)

        # Add Reserved - Present
        edge = self.interface.add_edge(n=rnode,v=rnode1,e=ids.predicates.has_part,graph_name=self.reserved_names)

        pre_n = list(self.interface.nodes)
        pre_e = list(self.interface.edges)
        self.interface.submit()
        post_n = list(self.interface.nodes)
        post_e = list(self.interface.edges)
        n_diff = list(set(post_n) - set(pre_n))
        e_diff = list(set(post_e) - set(pre_e))

        self.assertEqual(len(n_diff),0)
        self.assertEqual(len(e_diff),0)

        # Add Non-Reserved - Reserved Present.
        self.interface.add_edge(n=rnode2,v=rnode3,e=ids.predicates.has_part,graph_name=self.reserved_names)
        self.interface.submit()
        dge = self.interface.add_edge(n=node2,v=node3,e=ids.predicates.has_part,graph_name=[gn])

        pre_n = list(self.interface.nodes)
        pre_e = list(self.interface.edges)
        self.interface.submit()
        post_n = list(self.interface.nodes)
        post_e = list(self.interface.edges)
        n_diff = list(set(post_n) - set(pre_n))
        e_diff = list(set(post_e) - set(pre_e))

        self.assertEqual(len(n_diff),1)
        self.assertEqual(len(e_diff),1)
        self.assertCountEqual([node3],n_diff)
        self.assertCountEqual([dge],e_diff)

    def test_multiple_graphs(self):
        gnode = Node("node",ids.objects.physical_entity,graph_name=[gn])
        gnode1 = Node("node1",ids.objects.physical_entity,graph_name=[gn])

        g2node = Node("node",ids.objects.physical_entity,graph_name=[gn2])
        g2node1 = Node("node1",ids.objects.physical_entity,graph_name=[gn2])

        pre_n = list(self.interface.nodes)
        pre_e = list(self.interface.edges)
        self.interface.add_node(gnode)
        self.interface.add_node(gnode1)
        self.interface.submit()
        self.interface.add_node(g2node)
        self.interface.add_node(g2node1)
        self.interface.submit()
        self.interface.add_edge(gnode,gnode1,ids.predicates.has_part,graph_name=[gn])
        self.interface.submit()
        self.interface.add_edge(g2node,g2node1,ids.predicates.has_part,graph_name=[gn2])
        self.interface.submit()
        post_n = list(self.interface.nodes)
        post_e = list(self.interface.edges)
        n_diff = list(set(post_n) - set(pre_n))
        e_diff = list(set(post_e) - set(pre_e))

        self.assertEqual(len(n_diff),2)
        self.assertEqual(len(e_diff),1)

        for node in n_diff:
            self.assertEqual(node.graph_name,[gn,gn2])
        for e in e_diff:
            self.assertEqual(e.graph_name,[gn,gn2])


    def test_remove_graph(self):
        in_edges = [("key","key1","e_type")]
        for n,v,e in in_edges:
            n = self.interface.add_node(n,graph_name=[gn])
            v = self.interface.add_node(v,graph_name=[gn])
            self.interface.add_edge(n,v,e,graph_name = [gn])
            self.interface.submit()
        
        self.interface.remove_graph(gn)
        self.assertEqual(self.interface.node_query(graph_name=[gn]),[])

    def test_node(self):
        in_nodes = [("key","type")]
        for k,t in in_nodes:
            res = self.interface.add_node(k,graph_name=[gn])
            self.interface.submit()
            res_q = self.interface.node_query(k,graph_name=[gn])
            self.assertEqual(res,res_q[0])
            self.interface.add_node(k,graph_name=[gn2])
            self.interface.submit()
            gn_res = self.interface.node_query(graph_name=[gn])
            self.assertEqual(res,gn_res[0])
        self.interface.remove_graph(gn)
        self.assertEqual(self.interface.node_query(graph_name=[gn]),[])
        self.assertEqual(self.interface.node_query(graph_name=[gn2])[0].get_key(),in_nodes[0][0])
        self.interface.remove_graph(gn2)

    def test_edge(self):
        self.interface.remove_graph(gn)
        in_edges = [("key","key1","e_type")]
        for n,v,e in in_edges:
            nodey = self.interface.add_node(n,graph_name=[gn])
            self.interface.add_node(v,graph_name=[gn])
            res = self.interface.add_edge(n,v,e,graph_name = [gn])
            self.interface.submit()
            res_q = self.interface.edge_query(n,v,e)
            self.assertEqual(res,res_q[0])
            n = self.interface.add_node(n,graph_name=[gn2])
            v = self.interface.add_node(v,graph_name=[gn2])
            self.interface.submit()
            self.interface.add_edge(n,v,e,graph_name = [gn2])
            self.interface.submit()
            gn_res = self.interface.edge_query(e_props={"graph_name":[gn2]})
            self.assertEqual(res,gn_res[0])



        self.assertEqual(self.interface.edge_query(e_props={"graph_name":[gn2]})[0].get_type(),in_edges[0][2])
        self.interface.remove_graph(gn2)

        self.interface.remove_graph(gn)
        res = self.interface.edge_query(e_props={"graph_name":[gn]})
        self.assertEqual(res,[])