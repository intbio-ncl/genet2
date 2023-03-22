from graphdatascience.graph.graph_object import Graph
from neo4j.graph import Node as NeoNode
from app.graph.utility.graph_objects.node import Node
from app.graph.neo4j_interface.gds.query_builder import GDSQueryBuilder


def _normalise_gn(g):
    if isinstance(g,Graph):
        return g.name()
    return g
        
class Centrality:
    def __init__(self,interface,builder):
        self._interface = interface
        self._qry_builder = builder

    def page_rank(self, name):
        '''
        Wrapper for 
        https://neo4j.com/docs/graph-data-science/current/algorithms/page-rank/
        '''
        name = _normalise_gn(name)
        qry = self._qry_builder.page_rank(name)
        res = self._interface.driver.run_cypher(qry)
        return [{"node":self._interface.labels_to_node(r[1]["node"].labels),
                "score":r[1]["score"]} for r in res.iterrows()]

    def article_rank(self, name):
        '''
        Wrapper for 
        https://neo4j.com/docs/graph-data-science/current/algorithms/article-rank/
        '''
        name = _normalise_gn(name)
        qry = self._qry_builder.article_rank(name)
        res = self._interface.driver.run_cypher(qry)
        return [{"node":self._interface.labels_to_node(r[1]["node"].labels),
                "score":r[1]["score"]} for r in res.iterrows()]

    def eigenvector(self, name):
        '''
        Wrapper for 
        https://neo4j.com/docs/graph-data-science/current/algorithms/eigenvector-centrality/
        '''
        name = _normalise_gn(name)
        qry = self._qry_builder.eigenvector_centrality(name)
        res = self._interface.driver.run_cypher(qry)
        return [{"node":self._interface.labels_to_node(r[1]["node"].labels),
                "score":r[1]["score"]} for r in res.iterrows()]

    def betweenness(self, name):
        '''
        Wrapper for 
        https://neo4j.com/docs/graph-data-science/current/algorithms/betweenness-centrality/
        '''
        name = _normalise_gn(name)
        qry = self._qry_builder.betweenness_centrality(name)
        res = self._interface.driver.run_cypher(qry)
        return [{"node":self._interface.labels_to_node(r[1]["node"].labels),
                "score":r[1]["score"]} for r in res.iterrows()]

    def degree(self, name):
        '''
        Wrapper for 
        https://neo4j.com/docs/graph-data-science/current/algorithms/degree-centrality/
        '''
        name = _normalise_gn(name)
        qry = self._qry_builder.degree_centrality(name)
        res = self._interface.driver.run_cypher(qry)
        return [{"node":self._interface.labels_to_node(r[1]["node"].labels),
                "score":r[1]["score"]} for r in res.iterrows()]

    def closeness(self, name):
        '''
        Wrapper for 
        https://neo4j.com/docs/graph-data-science/current/algorithms/closeness-centrality/
        '''
        name = _normalise_gn(name)
        qry = self._qry_builder.closeness_centrality(name)
        res = self._interface.driver.run_cypher(qry)
        return [{"node":self._interface.labels_to_node(r[1]["node"].labels),
                "score":r[1]["score"]} for r in res.iterrows()]

    def harmonic(self, name):
        '''
        Wrapper for 
        https://neo4j.com/docs/graph-data-science/current/algorithms/harmonic-centrality/
        '''
        name = _normalise_gn(name)
        qry = self._qry_builder.harmonic_centrality(name)
        res = self._interface.driver.run_cypher(qry)
        return [{"node":self._interface.labels_to_node(r[1]["node"].labels),
                "centrality":r[1]["centrality"]} for r in res.iterrows()]

    def hits(self, name):
        '''
        Wrapper for 
        https://neo4j.com/docs/graph-data-science/current/algorithms/hits/
        '''
        name = _normalise_gn(name)
        qry = self._qry_builder.hits(name)
        res = self._interface.driver.run_cypher(qry)
        return [{"node":self._interface.labels_to_node(r[1]["node"].labels),
                "values":r[1]["values"]} for r in res.iterrows()]

    def celf_im(self, name):
        '''
        Wrapper for 
        https://neo4j.com/docs/graph-data-science/current/algorithms/influence-maximization/celf/
        '''
        name = _normalise_gn(name)
        qry = self._qry_builder.celf_influence_maximization(name)
        res = self._interface.driver.run_cypher(qry)
        return [{"node":self._interface.labels_to_node(r[1]["node"].labels),
                "spread":r[1]["spread"]} for r in res.iterrows()]

    def greedy_im(self, name):
        '''
        Wrapper for 
        https://neo4j.com/docs/graph-data-science/current/algorithms/influence-maximization/greedy/
        '''
        name = _normalise_gn(name)
        qry = self._qry_builder.greedy_influence_maximization(name)
        res = self._interface.driver.run_cypher(qry)
        return [{"node":self._interface.labels_to_node(r[1]["node"].labels),
                "spread":r[1]["spread"]} for r in res.iterrows()]

class CommunityDetection:
    def __init__(self,interface,builder):
        self._interface = interface
        self._qry_builder = builder

    def _normalise(self,res):
        f = []
        for r in res.iterrows():
            row = {}
            for k,v in r[1].items():
                if k == "node":
                    v = self._interface.labels_to_node(v.labels)
                row[k] = v

            f.append(row)
        return f

    def louvain(self, name):
        '''
        Wrapper for 
        https://neo4j.com/docs/graph-data-science/current/algorithms/louvain/
        '''
        name = _normalise_gn(name)
        qry = self._qry_builder.louvain(name)
        return self._normalise(self._interface.driver.run_cypher(qry))


    def label_propagation(self, name):
        '''
        Wrapper for 
        https://neo4j.com/docs/graph-data-science/current/algorithms/label-propagation/
        '''
        name = _normalise_gn(name)
        qry = self._qry_builder.label_propagation(name)
        return self._normalise(self._interface.driver.run_cypher(qry))

    def wcc(self, name):
        '''
        Wrapper for 
        https://neo4j.com/docs/graph-data-science/current/algorithms/wcc/
        '''
        name = _normalise_gn(name)
        qry = self._qry_builder.wcc(name)
        return self._normalise(self._interface.driver.run_cypher(qry))

    def triangle_count(self, name):
        '''
        Wrapper for 
        https://neo4j.com/docs/graph-data-science/current/algorithms/triangle-count/
        '''
        name = _normalise_gn(name)
        qry = self._qry_builder.triangle_count(name)
        return self._normalise(self._interface.driver.run_cypher(qry))

    def local_clustering_coefficient(self, name):
        '''
        Wrapper for 
        https://neo4j.com/docs/graph-data-science/current/algorithms/local-clustering-coefficient/
        '''
        name = _normalise_gn(name)
        qry = self._qry_builder.local_clustering_coefficient(name)
        return self._normalise(self._interface.driver.run_cypher(qry))

    def k1coloring(self, name):
        '''
        Wrapper for 
        https://neo4j.com/docs/graph-data-science/current/algorithms/k1coloring/
        '''
        name = _normalise_gn(name)
        qry = self._qry_builder.k1coloring(name)
        return self._normalise(self._interface.driver.run_cypher(qry))

    def modularity_optimization(self, name):
        '''
        Wrapper for 
        https://neo4j.com/docs/graph-data-science/current/algorithms/modularity-optimization/
        '''
        name = _normalise_gn(name)
        qry = self._qry_builder.modularity_optimization(name)
        return self._normalise(self._interface.driver.run_cypher(qry))

    def scc(self, name):
        '''
        Wrapper for 
        https://neo4j.com/docs/graph-data-science/current/algorithms/strongly-connected-components/
        '''
        name = _normalise_gn(name)
        qry = self._qry_builder.scc(name)
        return self._normalise(self._interface.driver.run_cypher(qry))

    def sllpa(self, name):
        '''
        Wrapper for 
        https://neo4j.com/docs/graph-data-science/current/algorithms/sllpa/
        '''
        name = _normalise_gn(name)
        qry = self._qry_builder.sllpa(name)
        return self._normalise(self._interface.driver.run_cypher(qry))

    def maxkcut(self, name):
        '''
        Wrapper for 
        https://neo4j.com/docs/graph-data-science/current/algorithms/approx-max-k-cut/
        '''
        name = _normalise_gn(name)
        qry = self._qry_builder.maxkcut(name)
        return self._normalise(self._interface.driver.run_cypher(qry))

class Similarity:
    def __init__(self,interface,builder):
        self._interface = interface
        self._qry_builder = builder

    def _normalise(self,res):
        f = []
        for r in res.iterrows():
            row = {}
            for k,v in r[1].items():
                if isinstance(v,NeoNode):
                    v = self._interface.labels_to_node(v.labels)
                row[k] = v

            f.append(row)
        return f
        
    def node(self, name):
        '''
        Wrapper for 
        https://neo4j.com/docs/graph-data-science/current/algorithms/node-similarity/
        '''
        name = _normalise_gn(name)
        qry = self._qry_builder.node_similarity(name)
        return self._normalise(self._interface.driver.run_cypher(qry))

class PathFinding:
    def __init__(self,interface,builder):
        self._interface = interface
        self._qry_builder = builder

    def _normalise_sp(self,res):
        if res is None or len(res) == 0:
            return []
        results = []
        for path in res.iterrows():
            path = path[1]
            path = {"totalCost":path["totalCost"],
                    "path" : [self._interface.labels_to_node(n.labels) for n in path["path"]]}
            results.append(path)
        return results
            
    def delta_asp(self, name, source, mode="stream"):
        name = _normalise_gn(name)
        qry = self._qry_builder.delta_all_shortest_paths(name, source, mode)
        res = self._interface.driver.run_cypher(qry)
        results = []
        for index, path in res.iterrows():
            f_path = []
            for element in path["path"]:
                f_path.append(self._interface.labels_to_node(element.labels))
            results.append({"totalCost":path["totalCost"], "path":f_path})
        return results

    def dijkstra_asp(self, name, source, mode="stream"):
        name = _normalise_gn(name)
        qry = self._qry_builder.dijkstra_all_shortest_paths(name, source, mode)
        res = self._interface.driver.run_cypher(qry)
        results = []
        for index, path in res.iterrows():
            f_path = []
            for element in path["path"]:
                f_path.append(self._interface.labels_to_node(element.labels))
            results.append({"totalCost":path["totalCost"], "path":f_path})
        return results

    def dijkstra_sp(self, name, source, dest, mode="stream"):
        name = _normalise_gn(name)
        qry = self._qry_builder.dijkstra_shortest_path(
            name, source, dest, mode)
        res = self._interface.driver.run_cypher(qry)
        return self._normalise_sp(res)

    def astar_sp(self, name, source, dest, latitude_property,longitude_property, mode="stream"):
        name = _normalise_gn(name)
        qry = self._qry_builder.astar_shortest_path(
            name, source, dest, latitude_property, longitude_property, mode)
        res = self._interface.driver.run_cypher(qry)
        return self._normalise_sp(res)

    def yens_sp(self, name, source, dest, k, mode="stream"):
        name = _normalise_gn(name)
        qry = self._qry_builder.yens_shortest_path(
            name, source, dest, k, mode)
        res = self._interface.driver.run_cypher(qry)
        return self._normalise_sp(res)

    def dfs(self, name, source, dest=None, mode="stream"):
        name = _normalise_gn(name)
        qry = self._qry_builder.dfs(name, source, dest, mode)
        res = self._interface.driver.run_cypher(qry)
        paths = []
        for path in res.iterrows():
            path = path[1]
            # If this isnt true is it the case when two paths of equal length are found?
            assert(len(path) == 1)
            path = path[0]
            if len(path.relationships) == 0:
                continue
            p = []
            for rel in path.relationships:
                p.append(self._interface.labels_to_node(rel.nodes[0].labels))
            p.append(self._interface.labels_to_node(path.end_node.labels))
            paths.append({"path":p})
        return paths


    def bfs(self, name, source, dest=None, mode="stream"):
        name = _normalise_gn(name)
        qry = self._qry_builder.bfs(name, source, dest, mode)
        res = self._interface.driver.run_cypher(qry)
        paths = []
        for path in res.iterrows():
            path = path[1]
            # If this isnt true is it the case when two paths of equal length are found?
            assert(len(path) == 1)
            path = path["path"]
            if len(path.relationships) == 0:
                continue
            p = []
            for rel in path.relationships:
                p.append(self._interface.labels_to_node(rel.nodes[0].labels))
            p.append(self._interface.labels_to_node(path.end_node.labels))
            paths.append({"path":p})
        return paths

class TPP:
    def __init__(self,interface,builder):
        self._interface = interface
        self._qry_builder = builder

    def adamic_adar(self, name, node1, node2):
        qry = self._qry_builder.adamic_adar(name, node1, node2)
        res = self._interface.driver.run_cypher(qry)

class Procedures():
    def __init__(self, interface):
        builder = GDSQueryBuilder()
        self.centrality = Centrality(interface,builder)
        self.community_detection = CommunityDetection(interface,builder)
        self.similarity = Similarity(interface,builder)
        self.path_finding = PathFinding(interface,builder)
        self.tpp = TPP(interface,builder)
        self.modes = ["stream","mutate","stats","write"]
