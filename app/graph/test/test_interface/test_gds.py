import sys
import os
import unittest

sys.path.insert(0, os.path.join(".."))
sys.path.insert(0, os.path.join("..",".."))
sys.path.insert(0, os.path.join("..","..",".."))
sys.path.insert(0, os.path.join("..","..","..",".."))
from neo4j_interface.interface import Neo4jInterface
curr_dir = os.path.dirname(os.path.realpath(__file__))

class TestProjectGDS(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.interface = Neo4jInterface()
        self.project = self.interface.project

    @classmethod
    def tearDownClass(self):
        pass

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
        in_edges = [("key","key1","e_type"),("key2","key3","e_type1")]
        for n,v,e in in_edges:
            res = self.interface.add_edge(n,v,e,graph_name = [gn])
            self.interface.submit()
        gn2 = "test2"
        gn = "test1"
        try:
            self.project.drop(gn)
            self.project.drop(gn2)
        except Exception:
            pass
        g,data = self.project.project(gn,["key","key1","key2","key3"],["e_type","e_type1"])
        res = self.project.sub_graph(gn,gn2,["key","key1"],["e_type"])
        self.assertEqual(res.node_count(),2)
        self.assertEqual(res.relationship_count(),1)
        self.project.drop(gn)
        self.project.drop(gn2)

    def test_mutate(self):
        gn = "test_mutate"
        nodes = ["node" + str(i) for i in range(0,5)]
        edges = []
        paths = []

        for node in nodes:
            self.interface.add_node(node,graph_name=[gn])
        for index,node in enumerate(nodes):
            if index == len(nodes) - 1:
                continue
            nn = nodes[index+1]
            edges.append((node,nn,f'{node} - {nn}'))
            paths.append(f'{node} - {nn}')
        for n,v,e in edges:
            res = self.interface.add_edge(n,v,e,graph_name=[gn])
            self.interface.submit()

        try:
            self.project.drop(gn)
        except ValueError:
            pass
        res = self.project.project(gn,nodes,paths)
        pr = self.project.mutate(gn,paths,"mut")
        self.assertEqual(len(pr["relationshipsWritten"]),1)
        self.project.drop(gn)
        self.interface.remove_graph(gn)

class TestGDSProcedures(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.interface = Neo4jInterface()
        self.project = self.interface.project
        self.procedures = self.interface.procedures

    @classmethod
    def tearDownClass(self):
        pass

    def _setup(self,gn):
        nodes = ["node" + str(i) for i in range(0,5)]
        edges = []
        paths = []

        for node in nodes:
            self.interface.add_node(node,graph_name=[gn])
        for index,node in enumerate(nodes):
            if index == len(nodes) - 1:
                continue
            nn = nodes[index+1]
            edges.append((node,nn,f'{node} - {nn}'))
            paths.append(f'{node} - {nn}')
        for n,v,e in edges:
            res = self.interface.add_edge(n,v,e,graph_name=[gn])
            self.interface.submit()

        try:
            self.project.drop(gn)
        except ValueError:
            pass
        res = self.project.project(gn,nodes,paths)
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
        pr = self.procedures.path_finding.delta_asp(gn,"node0")
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
        pr = self.procedures.path_finding.dijkstra_asp(gn,"node0")
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