import re
import json
import networkx as nx
from rdflib import RDF

from app.graphs.graph_objects.edge import Edge
from app.graphs.graph_objects.node import Node

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



class ViewGraph:
    def __init__(self, graph=None):
        self._graph = graph if graph else nx.MultiDiGraph()

    def resolve_node(func):
        def inner(self,n=None):
            if isinstance(n,Node):
                n = n.id
            return func(self,n)
        return inner
        
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

    def nodes(self):
        for n,data in self._graph.nodes(data=True):
            props = data.copy()
            labels = props["key"]
            del props["key"]
            yield Node(labels,id=n,**props)

    @resolve_node
    def edges(self,n=None):
        for n,v,e,d in self._graph.edges(n,keys=True,data=True):
            props = self._graph.nodes[n].copy()
            labels = props["key"]
            del props["key"]
            n = Node(labels,id=n,**props)

            props = self._graph.nodes[v].copy()
            labels = props["key"]
            del props["key"]
            v = Node(labels,id=v,**props)
            yield Edge(n,v,e,**d)

    @resolve_node
    def in_edges(self, node=None):
        for n,v,e,d in self._graph.in_edges(node,keys=True,data=True):
            props = self._graph.nodes[n].copy()
            labels = props["key"]
            del props["key"]
            n = Node(labels,id=n,**props)

            props = self._graph.nodes[v].copy()
            labels = props["key"]
            del props["key"]
            v = Node(labels,id=v,**props)
            yield Edge(n,v,e,**d)

    @resolve_node
    def out_edges(self, node=None):
        for n,v,e,d in self._graph.out_edges(node,keys=True,data=True):
            props = self._graph.nodes[n].copy()
            labels = props["key"]
            del props["key"]
            n = Node(labels,id=n,**props)

            props = self._graph.nodes[v].copy()
            labels = props["key"]
            del props["key"]
            v = Node(labels,id=v,**props)
            yield Edge(n,v,e,**d)
        
    def add_edge(self, edge):
        self._graph.add_edge(edge.n.id,edge.v.id,key="-".join(edge.labels),**edge.get_properties())

    def remove_edge(self, edge):
        self._graph.remove_edge(edge.n.id, edge.v.id, key="-".join(edge.labels))

    def remove_node(self, node):
        self._graph.remove_node(node.id)

    def merge_nodes(self, subject, nodes):
        for node in nodes:
            in_edges = list(self.in_edges(node))
            out_edges = list(self.out_edges(node))
            for edge in in_edges:
                self.remove_edge(edge)
                if edge.n != subject:
                    self.add_edge(Edge(edge.n, subject, edge.get_labels(), **edge.get_properties()))
            for edge in out_edges:
                self.remove_edge(edge)
                if edge.v != subject:
                    self.add_edge(Edge(subject,edge.v, edge.get_labels(), **edge.get_properties()))
            self.remove_node(node)

    def save(self, output=None, d_type="gexf"):
        try:
            return save_map[d_type](self._graph, output)
        except KeyError:
            return

    def serialise(self, d_type):
        try:
            return save_map[d_type](self._graph)
        except KeyError:
            return

    def get_save_formats(self):
        return list(save_map.keys())

    def remove_isolated_nodes(self):
        self._graph.remove_nodes_from(list(nx.isolates(self._graph)))

    def generate(self, d_type):
        try:
            return save_map[d_type](self._graph)
        except KeyError:
            return
            
    def graph_name_map(self,ret_max=False,edges=False):
        gn_map = {}
        all_graphs = []
        if edges:
            iterable = self.edges()
        else:
            iterable = self.nodes()

        for item in iterable:
            gn = item["graph_name"]
            if item in gn_map:
                gn_map[item] = gn_map[item] + [n for n in gn if n not in gn_map[item]]
            else:
                gn_map[item] = gn
            if ret_max:
                all_graphs = all_graphs + [n for n in gn if n not in all_graphs]

        if ret_max:
            return gn_map,list(set(all_graphs))
        return gn_map

    @resolve_node
    def degree(self, node):
        return self._graph.degree(node)

    @resolve_node
    def bfs(self, source):
        for n,v in nx.bfs_tree(self._graph, source).edges():
            props = self._graph.nodes[n].copy()
            labels = props["key"]
            del props["key"]
            n = Node(labels,id=n,**props)

            props = self._graph.nodes[v].copy()
            labels = props["key"]
            del props["key"]
            v = Node(labels,id=v,**props)
            yield n,v


    @resolve_node
    def dfs(self, source):
        for n,v,e,k in nx.dfs_tree(self._graph, source).edges(keys=True,data=True):
            yield Edge(n,v,e,**k)

    def node_connectivity(self):
        return nx.node_connectivity(self._graph)

    def degree_assortativity_coefficient(self):
        return nx.degree_assortativity_coefficient(self._graph)

    def triangles(self):
        g = nx.Graph(self._graph)
        return len(nx.triangles(g))

    def transitivity(self):
        g = nx.Graph(self._graph)
        return nx.transitivity(g)

    def average_clustering(self):
        g = nx.Graph(self._graph)
        return nx.average_clustering(g)

    def is_at_free(self):
        g = nx.Graph(self._graph)
        return nx.is_at_free(g)

    def is_bipartite(self):
        g = nx.Graph(self._graph)
        return nx.is_bipartite(g)

    def has_bridges(self):
        g = nx.Graph(self._graph)
        return nx.has_bridges(g)

    def is_chordal(self):
        g = nx.Graph(self._graph)
        return nx.is_chordal(g)

    def graph_number_of_cliques(self):
        g = nx.Graph(self._graph)
        return nx.graph_number_of_cliques(g)

    def is_strongly_connected(self):
        return nx.is_strongly_connected(self._graph)

    def number_strongly_connected_components(self):
        return nx.number_strongly_connected_components(self._graph)

    def is_weakly_connected(self):
        return nx.is_weakly_connected(self._graph)

    def number_weakly_connected_components(self):
        return nx.number_weakly_connected_components(self._graph)

    def is_attracting_component(self):
        return nx.is_attracting_component(self._graph)

    def number_attracting_components(self):
        return nx.number_attracting_components(self._graph)

    def diameter(self):
        try:
            return nx.diameter(self._graph)
        except nx.NetworkXError:
            return -1

    def radius(self):
        try:
            return nx.radius(self._graph)
        except nx.NetworkXError:
            return -1

    def is_eulerian(self):
        return nx.is_eulerian(self._graph)

    def is_semieulerian(self):
        return nx.is_semieulerian(self._graph)

    def is_aperiodic(self):
        return nx.is_aperiodic(self._graph)

    def is_biconnected(self):
        g = nx.Graph(self._graph)
        return nx.is_biconnected(g)

    def is_tree(self):
        return nx.is_tree(self._graph)

    def is_forest(self):
        return nx.is_forest(self._graph)

    def is_arborescence(self):
        return nx.is_arborescence(self._graph)

    def is_branching(self):
        return nx.is_branching(self._graph)

    def pagerank(self):
        g = nx.Graph(self._graph)
        return nx.pagerank(g)

    def degree_centrality(self):
        return nx.degree_centrality(self._graph)

    def closeness_centrality(self):
        return nx.closeness_centrality(self._graph)

    def betweenness_centrality(self):
        g = nx.Graph(self._graph)
        return nx.betweenness_centrality(g)

    def number_of_cliques(self):
        g = nx.Graph(self._graph)
        return nx.number_of_cliques(g)

    def clustering(self):
        g = nx.Graph(self._graph)
        return nx.clustering(g)

    def square_clustering(self):
        return nx.square_clustering(self._graph)

    @resolve_node
    def is_isolate(self, node):
        return nx.is_isolate(self._graph, node)

    def _get_name(self, subject):
        split_subject = self._split(subject)
        if len(split_subject[-1]) == 1 and split_subject[-1].isdigit():
            return split_subject[-2]
        elif len(split_subject[-1]) == 3 and _isfloat(split_subject[-1]):
            return split_subject[-2]
        else:
            return split_subject[-1]

    def _node_from_attr(self, attribute,generator):
        nodes = []
        for n, data in self.generator():
            if attribute in data.values():
                labels = data["key"].copy()
                del data["key"]
                nodes.append(Node(labels,id=n,**data))
        if nodes == []:
            raise ValueError("Unable to find.")
        return nodes

    def _split(self, uri):
        return re.split('#|\/|:', uri)

def _isfloat(x):
    try:
        float(x)
        return True
    except ValueError:
        return False
