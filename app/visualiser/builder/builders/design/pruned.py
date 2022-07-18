from rdflib import RDF
from app.visualiser.builder.builders.abstract_view import AbstractViewBuilder
from  app.graph.utility.model.model import model
from app.visualiser.viewgraph.viewgraph import ViewGraph

bl_pred = {str(model.identifiers.predicates.consistsOf),str(RDF.type)}
w_predicates = list({str(p) for p in model.identifiers.predicates} - bl_pred)
                    

class PrunedViewBuilder(AbstractViewBuilder):
    def __init__(self,graph):
        super().__init__(graph)

    def _subgraph(self, edges=[],nodes=[], new_graph=None):
        return ViewGraph(super()._subgraph(edges,nodes,new_graph))

    def build(self):
        edges = []
        for edge in self._graph.edges():
            if not edge.get_type() in w_predicates:
                continue
            edges.append(edge)
        return self._subgraph(edges)

