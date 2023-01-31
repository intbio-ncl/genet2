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
curr_dir = os.path.dirname(os.path.realpath(__file__))

class TestProjectGDS(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.interface = Neo4jInterface()
        self.project = self.interface.project

        self.nodes = [Node("node"+ str(i),graph_name=["TestProjectGDS"]) for i in range(0,5)]
        self.edges = []
        for index,node in enumerate(self.nodes):
            if index == len(self.nodes) - 1:
                continue
            nn = self.nodes[index+1]
            edge = Edge(node,nn,f'{node} - {nn}',**{"graph_name" : ["TestProjectGDS"] })
            self.edges.append(edge)
            res = self.interface.add_edge(edge.n,edge.v,edge.get_type(),**edge.get_properties())
            self.interface.submit()

    @classmethod
    def tearDownClass(self):
        self.interface.remove_graph("TestProjectGDS")

    def test_project(self):
        gn = "test_project"
        nodes = "*"
        edges = "*"
        try:
            self.project.drop(gn)
        except Exception:
            pass
        g,data = self.project.project(gn,nodes,edges)
        gns = self.project.names()
        self.assertTrue(g.name() in gns)
        g1 = self.project.get_graph(gn)
        self.assertEqual(g.name(),g1.name())
        self.project.drop(gn)

    def test_sub_graph(self):
        gn = "test_sub_graph"
        gn2 = "test2"
        gn = "test1"
        try:
            self.project.drop(gn)
            self.project.drop(gn2)
        except Exception:
            pass
        edge0 = self.edges[0]
        node00 = edge0.n
        node01 = edge0.v
        edge1 = self.edges[1]
        node10 = edge1.n
        node11 = edge1.v
        g,data = self.project.project(gn,[node00,node01,node10,node11],[edge0.get_type(),edge1.get_type()])
        res = self.project.sub_graph(gn,gn2,[node00,node01],[edge0.get_type()])
        self.assertEqual(res.node_count(),2)
        self.assertEqual(res.relationship_count(),1)
        self.project.drop(gn)
        self.project.drop(gn2)

    def test_mutate(self):
        gn = "test_mutate"
        paths = []

        for edge in self.edges:
            paths.append(f'{edge.n} - {edge.v}')

        try:
            self.project.drop(gn)
        except ValueError:
            pass
        for e in self.interface.edge_query():
            print(e)
        print("\n")
        for n in self.nodes:
            print(n)
        print("\n")
        print(paths)
        res = self.project.project(gn,self.nodes,paths)
        pr = self.project.mutate(gn,[paths],"mut")
        self.assertEqual(len(pr["relationshipsWritten"]),1)
        self.project.drop(gn)
        self.interface.remove_graph(gn)

class TestGDSProcedures(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.interface = Neo4jInterface()
        self.project = self.interface.project
        self.procedures = self.interface.procedures
        self.nodes = [Node("node"+ str(i),graph_name=["TestGDSProcedures"]) for i in range(0,5)]
        self.edges = []
        self.paths = []
        for index,node in enumerate(self.nodes):
            if index == len(self.nodes) - 1:
                continue
            nn = self.nodes[index+1]
            edge = Edge(node,nn,f'{node} - {nn}{index}',**{"graph_name" : ["TestGDSProcedures"] })
            self.edges.append(edge)
            e_t = f'{edge.n} - {edge.v}'
            res = self.interface.add_edge(edge.n,edge.v,e_t,**edge.get_properties())
            self.interface.submit()
            self.paths.append(e_t)


    @classmethod
    def tearDownClass(self):
        self.interface.remove_graph("TestGDSProcedures")

    def _setup(self,gn):
        try:
            self.project.drop(gn)
        except ValueError:
            pass
        res = self.project.project(gn,self.nodes,self.paths)
        self.assertTrue(res[1]["nodeCount"] > 0)
        self.assertTrue(res[1]["relationshipCount"] > 0)
        return res

    def _teardown(self,gn):
        self.project.drop(gn)
        self.interface.remove_graph(gn)

    def test_page_rank(self):
        gn = "test_page_rank"
        res = self._setup(gn)
        pr = self.procedures.centrality.page_rank(gn)
        self.assertEqual(len(pr),res[0].node_count())
        self._teardown(gn)

    def test_article_rank(self):
        gn = "article_rank"
        res = self._setup(gn)
        pr = self.procedures.centrality.article_rank(gn)
        self.assertEqual(len(pr),res[0].node_count())
        self._teardown(gn)
        
    def test_eigenvector_centrality(self):
        gn = "eigenvector"
        res = self._setup(gn)
        pr = self.procedures.centrality.eigenvector(gn)
        self.assertEqual(len(pr),res[0].node_count())
        self._teardown(gn)

    def test_betweenness_centrality(self):
        gn = "betweenness"
        res = self._setup(gn)
        pr = self.procedures.centrality.betweenness(gn)
        self.assertEqual(len(pr),res[0].node_count())
        self._teardown(gn)

    def test_degree_centrality(self):
        gn = "degree"
        res = self._setup(gn)
        pr = self.procedures.centrality.degree(gn)
        self.assertEqual(len(pr),res[0].node_count())
        self._teardown(gn)

    def test_closeness_centrality(self):
        gn = "closeness"
        res = self._setup(gn)
        pr = self.procedures.centrality.closeness(gn)
        self.assertEqual(len(pr),res[0].node_count())
        self._teardown(gn)

    def test_harmonic_centrality(self):
        gn = "harmonic"
        res = self._setup(gn)
        pr = self.procedures.centrality.harmonic(gn)
        self.assertEqual(len(pr),res[0].node_count())
        self._teardown(gn)

    def test_hits(self):
        gn = "hits"
        res = self._setup(gn)
        pr = self.procedures.centrality.hits(gn)
        self.assertEqual(len(pr),res[0].node_count())
        self._teardown(gn)

    def test_celf_influence_maximization(self):
        gn = "celf_im"
        res = self._setup(gn)
        pr = self.procedures.centrality.celf_im(gn)
        self.assertEqual(len(pr),3)
        self._teardown(gn)

    def test_greedy_influence_maximization(self):
        gn = "greedy_im"
        res = self._setup(gn)
        pr = self.procedures.centrality.greedy_im(gn)
        self.assertEqual(len(pr),3)
        self._teardown(gn)

    def test_louvain(self):
        gn = "louvain"
        res = self._setup(gn)
        pr = self.procedures.community_detection.louvain(gn)
        self.assertEqual(len(pr),res[0].node_count())
        self._teardown(gn)

    def test_label_propagation(self):
        gn = "label_propagation"
        res = self._setup(gn)
        pr = self.procedures.community_detection.label_propagation(gn)
        self.assertEqual(len(pr),res[0].node_count())
        self._teardown(gn)

    def test_wcc(self):
        gn = "wcc"
        res = self._setup(gn)
        pr = self.procedures.community_detection.wcc(gn)
        self.assertEqual(len(pr),res[0].node_count())
        self._teardown(gn)
               
    def test_triangle_count(self):
        gn = "triangle_count"
        res = self._setup(gn)
        pr = self.procedures.community_detection.triangle_count(gn)
        self.assertEqual(len(pr),res[0].node_count())
        self._teardown(gn)
               
    def test_local_clustering_coefficient(self):
        gn = "local_clustering_coefficient"
        res = self._setup(gn)
        pr = self.procedures.community_detection.local_clustering_coefficient(gn)
        self.assertEqual(len(pr),res[0].node_count())
        self._teardown(gn)
               
    def test_k1coloring(self):
        gn = "k1coloring"
        res = self._setup(gn)
        pr = self.procedures.community_detection.k1coloring(gn)
        self.assertEqual(len(pr),res[0].node_count())
        self._teardown(gn)

    def test_modularity_optimization(self):
        gn = "modularity_optimization"
        res = self._setup(gn)
        pr = self.procedures.community_detection.modularity_optimization(gn)
        self.assertEqual(len(pr),res[0].node_count())
        self._teardown(gn)
               
    def test_scc(self):
        gn = "scc"
        res = self._setup(gn)
        pr = self.procedures.community_detection.scc(gn)
        self.assertEqual(len(pr),res[0].node_count())
        self._teardown(gn)

    def test_sllpa(self):
        gn = "sllpa"
        res = self._setup(gn)
        pr = self.procedures.community_detection.sllpa(gn)
        self.assertEqual(len(pr),res[0].node_count())
        self._teardown(gn)
               
    def test_maxkcut(self):
        gn = "maxkcut"
        res = self._setup(gn)
        pr = self.procedures.community_detection.maxkcut(gn)
        self.assertEqual(len(pr),res[0].node_count())
        self._teardown(gn)

    def test_node_similarity(self):
        gn = "node"
        res = self._setup(gn)
        pr = self.procedures.similarity.node(gn)
        self.assertEqual(len(pr),0)
        self._teardown(gn)
    
    def test_delta_all_shortest_paths(self):
        gn = "delta_asp"
        res = self._setup(gn)
        pr = self.procedures.path_finding.delta_asp(gn,self.nodes[0].get_key())
        self.assertTrue(len(pr)>1)
        for path in pr:
            self.assertIn("path",path)
            self.assertIn("totalCost",path)
            self.assertIsInstance(path["totalCost"],float)
            self.assertIsInstance(path["path"],list)
        self._teardown(gn)

    def test_dijkstra_all_shortest_paths(self):
        gn = "dijkstra_asp"
        res = self._setup(gn)
        pr = self.procedures.path_finding.dijkstra_asp(gn,self.nodes[0])
        self.assertTrue(len(pr)>1)
        for path in pr:
            self.assertIn("path",path)
            self.assertIn("totalCost",path)
            self.assertIsInstance(path["totalCost"],float)
            self.assertIsInstance(path["path"],list)
        self._teardown(gn)

    def test_dijkstra_shortest_path(self):
        gn = "dijkstra_sp"
        res = self._setup(gn)
        pr = self.procedures.path_finding.dijkstra_sp(gn,"node0","node3")
        self.assertTrue(len(pr) == 1)
        pr = pr[0]
        pr = pr["path"]
        self.assertCountEqual([r.get_key() for r in pr],["node0","node1","node2","node3"])
        self._teardown(gn)

    def test_yens_shortest_path(self):
        gn = "yens_sp"
        res = self._setup(gn)
        pr = self.procedures.path_finding.yens_sp(gn,"node0","node3",1)
        self.assertTrue(len(pr) == 1)
        pr = pr[0]
        pr = pr["path"]
        self.assertCountEqual([r.get_key() for r in pr],["node0","node1","node2","node3"])
        self._teardown(gn)

    def test_bfs(self):
        gn = "bfs"
        res = self._setup(gn)
        pr = self.procedures.path_finding.bfs(gn,"node0","node3")
        self.assertTrue(len(pr) == 1)
        pr = pr[0]
        pr = pr["path"]
        self.assertCountEqual([r.get_key() for r in pr],["node0","node1","node2","node3"])
        self._teardown(gn)

    def test_dfs(self):
        gn = "dfs"
        res = self._setup(gn)
        pr = self.procedures.path_finding.dfs(gn,"node0","node3")
        self.assertTrue(len(pr) == 1)
        pr = pr[0]
        pr = pr["path"]
        self.assertCountEqual([r.get_key() for r in pr],["node0","node1","node2","node3"])
        self._teardown(gn)