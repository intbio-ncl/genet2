from app.graph.utility.graph_objects.edge import Edge
from app.graph.utility.graph_objects.node import Node
from app.graph.utility.model.model import model
from app.graph.truth_graph.modules.abstract_module import AbstractModule

confidence = str(model.identifiers.external.confidence)
p_synonym = str(model.identifiers.external.synonym)

class SynonymModule(AbstractModule):
    def __init__(self,truth_graph):
        super().__init__(truth_graph)
    
    def get(self,subject=None,synonym=None,threshold=90):
        e = Edge(n=subject,v=synonym,type=p_synonym)
        res = self._tg.edge_query(e=e)
        if len(res) != 0:
            return self._cast_condfidence(res)
        if synonym is not None:
            res = self._tg.node_query(name=synonym)
            if res != []:
                assert(len(res) == 1)
                return self._tg.edge_query(n=res[0],threshold=threshold)
        return []


    def positive(self,subject,synonym):
        subject = self._cast_node(subject)
        synonym = self._cast_node(synonym)
        # Check if the subject is in the graph.
        res = self._tg.edge_query(subject,e=p_synonym)
        if len(res) != 0:
            for edge in res:
                # Full edge exists.
                if synonym.get_key() == edge.v.get_key():
                    return self._update_confidence(res[0],self._standard_modifier)
            else:
                edge = Edge(subject,synonym,p_synonym)
                # New synonym to existing subject
                return self._add_new_edge(edge)
            
        # Check if the synonym is a name property
        res = self._tg.node_query(name=synonym)
        if len(res) != 0:
            for node in res:
                r_type = node.get_type()
                if r_type !=  "None":
                    n_syn = Node(subject.name)
                    edge = Edge(node,n_syn,p_synonym)
                    return self._change(edge,self._standard_modifier)
            # The synonym node exists, let it fall through.
        edge = Edge(subject,synonym,p_synonym)
        return self._add_new_edge(edge)


    def negative(self,subject,synonym):
        # Same as positive but without adding any new edges.
        subject = self._cast_node(subject)
        synonym = self._cast_node(synonym)
        res = self._tg.edge_query(subject,e=p_synonym)
        if len(res) != 0:
            for edge in res:
                if synonym.get_key() == edge.v.get_key():
                    return self._update_confidence(res[0],-self._standard_modifier)

        res = self._tg.node_query(name=synonym)
        if len(res) != 0:
            for node in res:
                r_type = node.get_type()
                if r_type !=  "None":
                    n_syn = Node(subject.name)
                    edge = Edge(node,n_syn,p_synonym)
                    return self._change(edge,-self._standard_modifier)

