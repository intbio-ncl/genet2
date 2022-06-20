import networkx as nx
from rdflib import RDF
import re

class AbstractBuilder:
    def __init__(self, graph):
        self._graph = graph

    def v_nodes(self):
        return self.view.nodes()

    def v_edges(self,n=None):
        return self.view.edges(n)

    def in_edges(self, n=None):
        return self.view.in_edges(n)

    def out_edges(self, n=None):
        return self.view.out_edges(n)

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

    def view_number_map(self,ret_max=False,edges=False):
        return self.view.graph_name_map(ret_max=ret_max,edges=edges)

    def get_namespace(self, uri):
        split_subject = _split(uri)
        if len(split_subject[-1]) == 1 and split_subject[-1].isdigit():
            name = split_subject[-2]
        else:
            name = split_subject[-1]
        return uri.split(name)[0]

def _split(uri):
    return re.split('#|\/|:', uri)
