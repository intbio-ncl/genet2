from app.graph.utility.graph_objects.edge import Edge
from app.graph.utility.graph_objects.node import Node
from app.graph.utility.model.model import model
from app.graph.truth_graph.modules.abstract_module import AbstractModule

confidence = str(model.identifiers.external.confidence)
p_derivative = str(model.identifiers.external.derivative)

class DerivativeModule(AbstractModule):
    def __init__(self,truth_graph):
        super().__init__(truth_graph)
    
    def get(self,subject=None,derivative=None,threshold=90):
        e = Edge(n=subject,v=derivative,type=p_derivative)
        res = self._tg.edge_query(e=e)
        if len(res) != 0:
            return self._cast_condfidence(res)
        return []


    def positive(self,subject,derivative,score):
        subject = self._cast_node(subject)
        derivative = self._cast_node(derivative)
        # Check if the subject is in the graph.
        if score < 1:
            score = int(score *100)
        res = self._tg.edge_query(n=subject,v=derivative,e=p_derivative)
        if len(res) != 0:
            assert(len(res) == 1)
            return self._update_confidence(res[0],score)
        edge = Edge(subject,derivative,p_derivative,name="Derivative")
        return self._add_new_edge(edge,score)


    def negative(self,subject,derivative):
        # Same as positive but without adding any new edges.
        subject = self._cast_node(subject)
        derivative = self._cast_node(derivative)
        res = self._tg.edge_query(subject,e=p_derivative)
        if len(res) != 0:
            for edge in res:
                if derivative.get_key() == edge.v.get_key():
                    return self._update_confidence(res[0],-self._standard_modifier)

