from operator import sub
import re
import json
import networkx as nx
from rdflib import URIRef, RDF


def _stringify_graph(G):
    ng = nx.MultiDiGraph()
    for n, v, k, d in G.edges(keys=True, data=True):
        n_data = G.nodes[n]
        v_data = G.nodes[v]

        ng.add_node(n, **{key: str(v) for key, v in n_data.items()})
        ng.add_node(v, **{key: str(v) for key, v in v_data.items()})
        ng.add_edge(n, v, str(k), **d)
    return ng


def _adj_list(G, output=None):
    if output is None:
        return "\n".join(nx.generate_adjlist(G))
    else:
        return nx.write_adjlist(G, output)


def _gexf(G, output=None):
    G = _stringify_graph(G)
    if output is None:
        return "\n".join(nx.generate_gexf(G))
    else:
        return nx.write_gexf(G, output)


def _gml(G, output=None):
    G = _stringify_graph(G)
    if output is None:
        return "\n".join(nx.generate_gml(G))
    else:
        return nx.write_gml(G, output)


def _graphml(G, output=None):
    G = _stringify_graph(G)
    if output is None:
        return "\n".join(nx.generate_graphml(G))
    else:
        return nx.write_graphml(G, output)


def _cytoscape(G, output=None):
    js = nx.cytoscape_data(G)
    if output is None:
        return json.dumps(js)
    with open(output, 'w') as outfile:
        json.dump(js, outfile)


save_map = {
    "adj-list": _adj_list,
    "gexf": _gexf,
    "gml": _gml,
    "graphml": _graphml,
    "cytoscape": _cytoscape,
}

class AbstractGraph:
    def __init__(self, graph=None):
        self.igc = 1 if graph else 0
        self._graph = graph if graph else nx.MultiDiGraph()

    def __len__(self):
        return len(self._graph)

    def __eq__(self, obj):
        if isinstance(obj, self.__class__):
            return nx.is_isomorphic(self._graph, obj._graph)
        if isinstance(obj, nx.MultiDiGraph):
            return nx.is_isomorphic(self._graph, obj)
        return False

    def __iter__(self):
        for n in self._graph.nodes:
            yield n

    @property
    def nodes(self):
        return self._graph.nodes

    @property
    def edges(self):
        return self._graph.edges

    @property
    def graph(self):
        return self._graph

    @graph.setter
    def graph(self, graph):
        self._graph = graph

    def save(self, output=None, d_type="gexf"):
        try:
            return save_map[d_type](self._graph, output)
        except KeyError:
            return

    def generate(self, d_type):
        try:
            return save_map[d_type](self._graph)
        except KeyError:
            return

    def get_save_formats(self):
        return list(save_map.keys())

    def in_edges(self, node=None, keys=False, data=False):
        return self.graph.in_edges(node, keys=keys, data=data)

    def out_edges(self, node=None, keys=False, data=False):
        return self.graph.out_edges(node, keys=keys, data=data)

    def has_edge(self, n, v, e=None, k={}):
        return self.graph.has_edge(n, v, key=e, *k)

    def get_edge_data(self, n, v, e):
        return self.get_edge_data(n, v, e)

    def search(self, pattern, lazy=False,label_key="key"):
        matches = []
        s, p, o = pattern
        if not isinstance(s, (list, set, tuple)):
            s = [s]
        if p and not isinstance(p, (list, set, tuple)):
            p = [p]
        if o and not isinstance(o, (list, set, tuple)):
            o = [o]
        for subject in s:
            if subject is not None and subject not in self.nodes:
                subject = self._node_from_attr(subject)
            else:
                subject = [subject]
            for ns in subject:
                for n, v, k in self.edges(ns, keys=True):
                    if not p or k in p:
                        n_data = self.nodes[n]
                        v_data = self.nodes[v]
                        if not o or v_data[label_key] in o or v in o:
                            if lazy:
                                return ([n, n_data], [v, v_data], k)
                            matches.append(([n, n_data], [v, v_data], k))
        return matches

    def add_graph(self,graph):
        index = self._get_next_index()
        self.igc += 1
        gn = self.igc
        cur_graph_map = {}

        def _handle_node(d,data):
            nonlocal index
            if data["key"] in cur_graph_map:
                d = cur_graph_map[data["key"]]
            else:
                d = index
                index +=1
                data["graph_number"] = gn
                cur_graph_map[data["key"]] = d

            self.add_node(d,data)
            return d

        for n, v, e, k in graph.edges(keys=True, data=True):
            n_data = graph.nodes[n]
            v_data = graph.nodes[v]

            n = _handle_node(n,n_data)
            v = _handle_node(v,v_data)
            k["graph_number"] = gn
            self.add_edge(n,v,e,**k)
        
    def add_node(self, n, data):
        self._graph.add_node(n, **data)

    def add_edge(self, n1, n2, key, **kwargs):
        self._graph.add_edge(n1, n2, key=key, **kwargs)

    def remove_node(self, node):
        self._graph.remove_node(int(node))

    def remove_edge(self, n, v, e):
        self._graph.remove_edge(n, v, key=e)

    def remove_isolated_nodes(self):
        self._graph.remove_nodes_from(list(nx.isolates(self._graph)))

    def merge_nodes(self, subject, nodes):
        subject = int(subject)
        for node in nodes:
            node = int(node)
            in_edges = list(self.in_edges(node, keys=True, data=True))
            out_edges = list(self.out_edges(node, keys=True, data=True))
            for n, _, e, d in in_edges:
                self.remove_edge(n, node, e)
                if n != subject:
                    self.add_edge(n, subject, e, **d)
            for _, v, e, d in out_edges:
                self.remove_edge(node, v, e)
                if v != subject:
                    self.add_edge(subject, v, e, **d)
            self.remove_node(node)

    def degree(self, node):
        return self.graph.degree(node)

    def get_rdf_type(self, subject):
        rdf_type = self.search((subject, RDF.type, None), lazy=True)
        if rdf_type != []:
            return rdf_type[1]

    def bfs(self, source):
        return nx.bfs_tree(self._graph, source).edges()

    def dfs(self, source):
        return nx.dfs_tree(self._graph, source).edges()

    def node_connectivity(self):
        return nx.node_connectivity(self.graph)

    def degree_assortativity_coefficient(self):
        return nx.degree_assortativity_coefficient(self.graph)

    def triangles(self):
        g = nx.Graph(self.graph)
        return len(nx.triangles(g))

    def transitivity(self):
        g = nx.Graph(self.graph)
        return nx.transitivity(g)

    def average_clustering(self):
        g = nx.Graph(self.graph)
        return nx.average_clustering(g)

    def is_at_free(self):
        g = nx.Graph(self.graph)
        return nx.is_at_free(g)

    def is_bipartite(self):
        g = nx.Graph(self.graph)
        return nx.is_bipartite(g)

    def has_bridges(self):
        g = nx.Graph(self.graph)
        return nx.has_bridges(g)

    def is_chordal(self):
        g = nx.Graph(self.graph)
        return nx.is_chordal(g)

    def graph_number_of_cliques(self):
        g = nx.Graph(self.graph)
        return nx.graph_number_of_cliques(g)

    def is_strongly_connected(self):
        return nx.is_strongly_connected(self.graph)

    def number_strongly_connected_components(self):
        return nx.number_strongly_connected_components(self.graph)

    def is_weakly_connected(self):
        return nx.is_weakly_connected(self.graph)

    def number_weakly_connected_components(self):
        return nx.number_weakly_connected_components(self.graph)

    def is_attracting_component(self):
        return nx.is_attracting_component(self.graph)

    def number_attracting_components(self):
        return nx.number_attracting_components(self.graph)

    def diameter(self):
        try:
            return nx.diameter(self.graph)
        except nx.NetworkXError:
            return -1

    def radius(self):
        try:
            return nx.radius(self.graph)
        except nx.NetworkXError:
            return -1

    def is_eulerian(self):
        return nx.is_eulerian(self.graph)

    def is_semieulerian(self):
        return nx.is_semieulerian(self.graph)

    def is_aperiodic(self):
        return nx.is_aperiodic(self.graph)

    def is_biconnected(self):
        g = nx.Graph(self.graph)
        return nx.is_biconnected(g)

    def is_tree(self):
        return nx.is_tree(self.graph)

    def is_forest(self):
        return nx.is_forest(self.graph)

    def is_arborescence(self):
        return nx.is_arborescence(self.graph)

    def is_branching(self):
        return nx.is_branching(self.graph)

    def pagerank(self):
        g = nx.Graph(self.graph)
        return nx.pagerank(g)

    def degree_centrality(self):
        return nx.degree_centrality(self.graph)

    def closeness_centrality(self):
        return nx.closeness_centrality(self.graph)

    def betweenness_centrality(self):
        g = nx.Graph(self.graph)
        return nx.betweenness_centrality(g)

    def number_of_cliques(self):
        g = nx.Graph(self.graph)
        return nx.number_of_cliques(g)

    def clustering(self):
        g = nx.Graph(self.graph)
        return nx.clustering(g)

    def square_clustering(self):
        return nx.square_clustering(self.graph)

    def is_isolate(self, node):
        return nx.is_isolate(self.graph, node)

    def _get_next_index(self):
        if len(self.nodes) == 0:
            return 0
        return max([i for i in self.nodes]) + 1

    def _get_name(self, subject):
        split_subject = self._split(subject)
        if len(split_subject[-1]) == 1 and split_subject[-1].isdigit():
            return split_subject[-2]
        elif len(split_subject[-1]) == 3 and _isfloat(split_subject[-1]):
            return split_subject[-2]
        else:
            return split_subject[-1]

    def _node_from_attr(self, attribute):
        nodes = []
        for n, data in self.nodes(data=True):
            if attribute in data.values():
                nodes.append(n)
        if nodes == []:
            raise ValueError("Unable to find.")
        return nodes

    def _split(self, uri):
        return re.split('#|\/|:', uri)

    def _generate_labels(self):
        for node, data in self.nodes(data=True):
            if "display_name" not in data.keys():
                identity = data["key"]
                if isinstance(identity, URIRef):
                    name = self._get_name(identity)
                else:
                    name = str(identity)
                self.nodes[node]["display_name"] = name

        for n, v, k, e in self.edges(keys=True, data=True):
            if "display_name" not in e.keys():
                e["display_name"] = self._get_name(k)


def _isfloat(x):
    try:
        float(x)
        return True
    except ValueError:
        return False
