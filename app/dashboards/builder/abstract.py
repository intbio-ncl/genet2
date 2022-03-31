import networkx as nx
from rdflib import RDF
import re


class AbstractBuilder:
    def __init__(self, graph,view_class):
        self._graph = graph
        self.view = view_class()
        self.connect_label = "key"

    def nodes(self):
        return self._graph.get_all_nodes()

    def edges(self):
        return self._graph.get_all_edges()

    def v_nodes(self):
        return self.view.nodes()

    def v_edges(self,n=None):
        return self.view.edges(n)

    def in_edges(self, n=None):
        return self.view.in_edges(n)

    def out_edges(self, n=None):
        return self.view.out_edges(n)

    def get_rdf_type(self, node=None):
        return self._graph.edge_query(n=node,e=RDF.type)


    def set_full_view(self):
        self.view = self._view_h.full()
        
    def set_network_mode(self):
        self.view = self._mode_h.network()

    def set_tree_mode(self):
        self.view = self._mode_h.tree()

    def set_union_mode(self):
        self.view = self._mode_h.union()

    def set_node_difference_mode(self):
        self.view = self._mode_h.node_difference()

    def set_edge_difference_mode(self):
        self.view = self._mode_h.edge_difference()

    def set_node_intersection_mode(self):
        self.view = self._mode_h.node_intersection()

    def set_edge_intersection_mode(self):
        self.view = self._mode_h.edge_intersection()

    def sub_graph(self, edges=[], new_graph=None):
        if not new_graph:
            new_graph = nx.MultiDiGraph()
            for e in edges:
                n = e.n
                v = e.v
                e_key = "-".join(e.get_labels())
                n.add_property("key","-".join(n.get_labels()))
                v.add_property("key","-".join(v.get_labels()))
                new_graph.add_node(n.id,**n.get_properties())
                new_graph.add_node(v.id,**v.get_properties())
                new_graph.add_edge(n.id,v.id,e_key,**e.get_properties())
        new_graph = self.view.__class__(new_graph)
        return new_graph

    def view_number_map(self,ret_max=False,edges=False):
        return self.view.graph_name_map(ret_max=ret_max,edges=edges)

    def get_namespace(self, uri):
        split_subject = _split(uri)
        if len(split_subject[-1]) == 1 and split_subject[-1].isdigit():
            name = split_subject[-2]
        else:
            name = split_subject[-1]
        return uri.split(name)[0]

    def resolve_list(self, list_node):
        elements = []
        next_node = list_node
        while True:
            res = self._graph.edge_query(n=next_node)
            f = [c for c in res if str(RDF.first) in c.get_labels()]
            r = [c for c in res if str(RDF.rest) in c.get_labels()]
            if len(f) != 1 or len(r) != 1:
                raise ValueError(f'{list_node} is a malformed list.')
            elements.append(f[0])
            r = r[0]
            if str(RDF.nil) in r.v.get_labels():
                break
            next_node = r.v
        return elements


def _split(uri):
    return re.split('#|\/|:', uri)
