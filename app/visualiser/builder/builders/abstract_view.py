import re
import networkx as nx
class AbstractViewBuilder:
    def __init__(self,graph):
        self._graph = graph

    def set_graph(self,graph):
        self._graph = graph

    def full(self):
        return self._subgraph(self._graph.edges())

    def _subgraph(self, edges=[], new_graph=None):
        if not new_graph:
            new_graph = nx.MultiDiGraph()
            for e in edges:
                n = e.n
                v = e.v
                e_key = e.get_type()
                new_graph.add_node(n.id,key=n.get_key(),type=n.get_type(),**n.get_properties())
                new_graph.add_node(v.id,key=v.get_key(),type=v.get_type(),**v.get_properties())
                new_graph.add_edge(n.id,v.id,e_key,**e.get_properties())
        return new_graph

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