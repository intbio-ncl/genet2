import re
from abc import ABC
from app.graph.utility.model.model import model
from app.graph.utility.graph_objects.edge import Edge
from app.graph.utility.graph_objects.node import Node

confidence = str(model.identifiers.external.confidence)
p_synonym = str(model.identifiers.external.synonym)

class AbstractModule(ABC):
    def __init__(self,truth_graph):
        self._tg = truth_graph
        self._standard_modifier = 5
        self._upper_threshold = 100
        self._lower_threshold = 0
    
    def positive(self,edges):
        return self._change(edges,self._standard_modifier)
    
    def negative(self,edges):
        return self._change(edges,-self._standard_modifier)

    def get(self,edge):
        res = self._tg.edge_query(e=edge)
        if len(res) == 0:
            return None
        res = self._cast_condfidence(res)
        assert(len(res) == 1)
        return res[0]

    
    def upper_threshold(self):
        pass
    
    def _cast_edge(self,edge):
        n = self._cast_node(edge.n)
        v = self._cast_node(edge.v)
        edge.n = n
        edge.v = v
        edge.properties["graph_name"] = self._tg.name
        edge.graph_name = self._tg.name
        return edge
        
    def _cast_node(self,subject):
        if not isinstance(subject,Node):
            subject = Node(subject)
        subject.properties["graph_name"] = self._tg.name
        subject.graph_name = self._tg.name
        return subject

    def _change(self,edges,modifier):
        if not isinstance(edges,(list,set,tuple)):
            edges = [edges]
        for edge in edges:
            if not isinstance(edge,Edge):
                raise ValueError(f'{edge} must be an edge.')
            eq = self._tg.edge_query(e=edge)
            if eq != []:
                eq = self._cast_condfidence(eq)
                assert(len(eq) == 1)
                eq = eq[0]
                self._update_confidence(eq,modifier)
                continue
            # Don't add feedback with no confidence.
            if modifier > 0:
                self._add_new_edge(edge)

    def _add_new_edge(self,edge):
        nq = self._tg.node_query([edge.n,edge.v])
        if nq != []:
            assert(edge.n in nq or edge.v in nq)
            if edge.n not in nq:
                self._tg.add_node(edge.n)
            if edge.v not in nq:
                self._tg.add_node(edge.n)
        self._tg.add_edge(edge,self._standard_modifier)

    def _update_confidence(self,edge,modifier):
        conf = edge.get_properties()[confidence]
        new_conf = int(conf) + modifier
        if new_conf >= self._upper_threshold:
            self._tg.set_confidence(edge,100)
            self._upper_change(edge)
        elif new_conf <= self._lower_threshold:
            self._lower_change(edge)
        else:
            self._tg.set_confidence(edge,new_conf)

    def _upper_change(self,edge):
        pass

    def _lower_change(self,edge):
        nedges = self._tg.edge_query(n=edge.n,directed=False)
        vedges = self._tg.edge_query(n=edge.v,directed=False)
        if len(nedges) == 1:
            self._tg.remove_node(edge.n)
        if len(vedges) == 1:
            self._tg.remove_node(edge.v)
        self._tg.remove_edge(edge)

    def _cast_condfidence(self,res):
        for r in res:
            c_val = int(r[confidence])
            r.update({confidence : c_val})
            setattr(r,"confidence",c_val)
        return res