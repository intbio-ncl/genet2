from collections import Counter
from itertools import chain
import re
import networkx as nx
from app.graphs.graph_objects.node import Node
from app.graphs.graph_objects.edge import Edge

class AbstractModeBuilder:
    def __init__(self,builder):
        self._builder = builder
    
    def tree(self):
        tree_edges = []
        seen = []
        v_nodes = [*self._builder.v_nodes()]
        if len(v_nodes) == 0:
            return self._builder.sub_graph(tree_edges)
            
        for edge in self._builder.v_edges():
            if edge in seen:
                new_n = edge.n.duplicate()
                new_v = edge.v.duplicate()
                new_e = Edge(new_n,new_v,edge.get_labels(),**edge.get_properties())
                tree_edges.append(new_e)
            else:
                seen.append(edge)
            tree_edges.append(edge)       
        tree_graph = self._builder.sub_graph(tree_edges)
        return tree_graph

    def network(self):
        return self._builder.view

    def union(self):
        edges = []
        seens = {}
        def swap(node):
            if node in seens:
                node = seens[node]
            else:
                seens[node] = node
            return node
        for edge in self._builder.v_edges():
            edge.n = swap(edge.n)
            edge.v = swap(edge.v)            
            edges.append(edge)
        return self._builder.sub_graph(edges)

    def node_intersection(self):
        '''
        Check if the number of occurances of a node is equal to number of graphs.
        '''
        edges = []
        gn_map,all_names = self._builder.view_number_map(ret_max=True)
        seens = {}
        def valid(node):
            assert(node in gn_map)
            agn = gn_map[node]
            if len(agn) == len(all_names):
                return True
            return False

        def swap(node):
            if node in seens:
                node = seens[node]
            else:
                seens[node] = node
            return node

        for edge in self._builder.v_edges():
            if edge not in edges and valid(edge.n) and valid(edge.v):
                edge.n = swap(edge.n)
                edge.v = swap(edge.v)
                edges.append(edge)
        return self._builder.sub_graph(edges)

    def edge_intersection(self):
        edges = []
        gn_map,all_names = self._builder.view_number_map(ret_max=True,edges=True)
        seens = {}
        def valid(item):
            assert(item in gn_map)
            agn = gn_map[item]
            if len(agn) == len(all_names):
                return True
            return False

        def swap(node):
            if node in seens:
                node = seens[node]
            else:
                seens[node] = node
            return node

        for edge in self._builder.v_edges():
            if edge not in edges and valid(edge):
                edge.n = swap(edge.n)
                edge.v = swap(edge.v)
                edges.append(edge)
        return self._builder.sub_graph(edges)

    def node_difference(self):
        '''
        Check if the number of occurances of a node is equal to 1.
        '''
        edges = []
        gn_map = self._builder.view_number_map()
        seens = {}
        def valid(node):
            assert(node in gn_map)
            agn = gn_map[node]
            if len(agn) == 1:
                return True
            return False

        def swap(node):
            if node in seens:
                node = seens[node]
            else:
                seens[node] = node
            return node

        for edge in self._builder.v_edges():
            if edge not in edges and valid(edge.n) and valid(edge.v):
                edge.n = swap(edge.n)
                edge.v = swap(edge.v)
                edges.append(edge)
        return self._builder.sub_graph(edges)
        
    def edge_difference(self):
        edges = []
        gn_map = self._builder.view_number_map(edges=True)
        seens = {}
        def valid(item):
            assert(item in gn_map)
            agn = gn_map[item]
            if len(agn) == 1:
                return True
            return False

        def swap(node):
            if node in seens:
                node = seens[node]
            else:
                seens[node] = node
            return node

        for edge in self._builder.v_edges():
            if edge not in edges and valid(edge):
                edge.n = swap(edge.n)
                edge.v = swap(edge.v)
                edges.append(edge)
        return self._builder.sub_graph(edges)

    def _create_edge_dict(self,key,weight=1,**kwargs):
        edge = {'weight': weight, 
                'name': self._get_name(str(key))}
        edge.update(kwargs)
        return edge

    def _get_name(self,subject):
        split_subject = self._split(subject)
        if len(split_subject[-1]) == 1 and split_subject[-1].isdigit():
            return split_subject[-2]
        elif len(split_subject[-1]) == 3 and _isfloat(split_subject[-1]):
            return split_subject[-2]
        else:
            return split_subject[-1]

    def _split(self,uri):
        return re.split('#|\/|:', uri)

def _isfloat(x):
    try:
        float(x)
        return True
    except ValueError:
        return False