import networkx as nx
from rdflib import RDF
import re


class AbstractBuilder:
    def __init__(self, graph):
        self._graph = graph
        self.view = self._graph
        self.connect_label = "key"

    @property
    def nodes(self):
        return self._graph.nodes

    @property
    def edges(self):
        return self._graph.edges

    @property
    def v_nodes(self):
        return self.view.nodes

    @property
    def v_edges(self):
        return self.view.edges

    @property
    def graph(self):
        return self.view

    def get_node_data(self, node_id):
        node_id = self._resolve_subject(node_id)
        try:
            return self.nodes[node_id]
        except KeyError:
            pass
        try:
            return self.v_nodes[node_id]
        except KeyError:
            return None

    def get_next_index(self):
        return max([i for i in self._graph.nodes])

    def in_edges(self, node=None, keys=False):
        return self.view.in_edges(node, keys=keys)

    def out_edges(self, node=None, keys=False):
        return self.view.out_edges(node, keys=keys)

    def set_network_mode(self):
        self.view = self._mode_h.network()

    def set_tree_mode(self):
        self.view = self._mode_h.tree()

    def set_union_mode(self):
        self.view = self._mode_h.union()

    def set_full_view(self):
        self.view = self._view_h.full()

    def set_node_difference_mode(self):
        self.view = self._mode_h.node_difference()

    def set_edge_difference_mode(self):
        self.view = self._mode_h.edge_difference()

    def set_node_intersection_mode(self):
        self.view = self._mode_h.node_intersection()

    def set_edge_intersection_mode(self):
        self.view = self._mode_h.edge_intersection()

    def sub_graph(self, edges=[], node_attrs={}, new_graph=None):
        if not new_graph:
            new_graph = nx.MultiDiGraph()
            new_graph.add_edges_from(edges)
            for k, v in node_attrs.items():
                new_graph.add_node(k, **v)
        new_graph = self._graph.__class__(new_graph)
        new_graph.igc = self._graph.igc
        return new_graph

    def get_rdf_type(self, subject):
        subject = self._resolve_subject(subject)
        return self._graph.get_rdf_type(subject)

    def get_internal_graphs(self, create_graphs=True, keys_as_ids=False,key="key"):
        if create_graphs:
            graphs = [nx.MultiDiGraph() for index in range(0, self._graph.igc)]
        else:
            graphs = [({}, []) for index in range(0, self._graph.igc)]
        seens = {}
        for n, v, e, k in self.edges(keys=True, data=True):
            n_data = self.nodes[n]
            v_data = self.nodes[v]

            assert(n_data["graph_number"] ==
                   v_data["graph_number"] == k["graph_number"])
            cg = graphs[k["graph_number"]-1]

            if n_data[self.connect_label] in seens:
                n = seens[n_data[self.connect_label]]
            else:
                if keys_as_ids:
                    n = n_data[key]
                seens[n_data[self.connect_label]] = n
            if v_data[self.connect_label] in seens:
                v = seens[v_data[self.connect_label]]
            else:
                if keys_as_ids:
                    v = v_data[key]
                seens[v_data[self.connect_label]] = v

            if create_graphs:
                cg.add_node(n, **n_data)
                cg.add_node(v, **v_data)
                cg.add_edge(n, v, e, **k)
            else:
                if n in cg[0]:
                    cg[0][n].update(n_data)
                else:
                    cg[0][n] = n_data

                if v in cg[0]:
                    cg[0][v].update(v_data)
                else:
                    cg[0][v] = v_data
                cg[1].append((n_data[self.connect_label], v_data[self.connect_label], e, k))
        return graphs
    """
    def add_view_graph_numbers(self):
        '''
        Goal: For each n,v,e in graph get the graph number.
        Nodes already have gns. However, there will likely be duplicates.
        Can't assume edge will be in main graph.
        '''
        for n, v, e, k in self.v_edges(keys=True, data=True):
            n_data = self.nodes[n]
            v_data = self.nodes[v]
            print(n_data)
            print(v_data)
            print(e)
            print(k)
            print("\n\n")
            graph_number = []
            k["graph_number"] = graph_number
    """
            
    def get_namespace(self, uri):
        split_subject = _split(uri)
        if len(split_subject[-1]) == 1 and split_subject[-1].isdigit():
            name = split_subject[-2]
        else:
            name = split_subject[-1]
        return uri.split(name)[0]

    def resolve_list(self, list_id):
        elements = []
        list_id = self._resolve_subject(list_id)
        next_id = list_id
        while True:
            res = self._graph.search((next_id, None, None))
            f = [c[1] for c in res if c[2] == RDF.first]
            r = [c[1] for c in res if c[2] == RDF.rest]
            if len(f) != 1 or len(r) != 1:
                raise ValueError(f'{list_id} is a malformed list.')
            elements.append(f[0])
            r, r_data = r[0]
            if r_data["key"] == RDF.nil:
                break
            next_id = r
        return elements

    def _resolve_subject(self, subject):
        if subject in self._graph:
            return subject
        if subject in self.view:
            key = self.view.nodes[subject]["key"]
            for n, data in self._graph.nodes(data=True):
                if data["key"] == key:
                    return n
            else:
                return subject
        raise ValueError(f'{subject} Not in either graph or viewgraph.')


def _split(uri):
    return re.split('#|\/|:', uri)
