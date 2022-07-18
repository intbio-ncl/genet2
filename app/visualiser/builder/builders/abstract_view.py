import networkx as nx

class AbstractViewBuilder():
    def __init__(self,graph):
        self._graph = graph

    def set_graph(self,graph):
        self._graph = graph

    def _subgraph(self, edges=[], nodes=[],new_graph=None):
        if not new_graph:
            new_graph = nx.MultiDiGraph()
            for e in edges:
                n = e.n
                v = e.v
                e_key = e.get_type()
                new_graph.add_node(n.id,key=n.get_key(),type=n.get_type(),**n.get_properties())
                new_graph.add_node(v.id,key=v.get_key(),type=v.get_type(),**v.get_properties())
                new_graph.add_edge(n.id,v.id,e_key,**e.get_properties())
            for n in nodes:
                new_graph.add_node(n.id,key=n.get_key(),type=n.get_type(),**n.get_properties())
        return new_graph