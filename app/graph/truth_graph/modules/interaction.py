from app.graph.utility.graph_objects.edge import Edge
from app.graph.utility.graph_objects.node import Node
from app.graph.utility.model.model import model
from app.graph.truth_graph.modules.abstract_module import AbstractModule

confidence = str(model.identifiers.external.confidence)

class InteractionModule(AbstractModule):
    def __init__(self,truth_graph):
        super().__init__(truth_graph)
    
    def get(self,subject=None,object=None,interaction=None,threshold=90):
        if interaction is None:
            interaction = [str(f[1]["key"]) for f in model.interaction_predicates()]
        if not isinstance(interaction,list):
            interaction = [interaction]
        res = []
        for i in interaction:
            e = Edge(n=subject,v=object,type=i)
            res += self._tg.edge_query(e=e)
        if len(res) != 0:
            return self._cast_condfidence(res)
        return []

    def positive(self,n,v,e):
        edge = self._cast_edge(n,v,e)
        # Check if the subject is in the graph.
        res = self._tg.edge_query(n=edge.n,v=edge.v,e=edge.get_type())
        if len(res) != 0:
            assert(len(res) == 1)
            return self._update_confidence(res[0],self._standard_modifier)
        else:
            return self._add_new_edge(edge)
            
    def negative(self,n,v,e):
        edge = self._cast_edge(n,v,e)
        # Check if the subject is in the graph.
        res = self._tg.edge_query(n=edge.n,v=edge.v,e=edge.get_type())
        if len(res) != 0:
            assert(len(res) == 1)
            return self._update_confidence(res[0],-self._standard_modifier)

