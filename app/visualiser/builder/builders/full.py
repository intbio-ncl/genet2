from app.visualiser.builder.builders.abstract_view import AbstractViewBuilder
from app.visualiser.viewgraph.viewgraph import ViewGraph
class FullViewBuilder(AbstractViewBuilder):
    def __init__(self,graph):
        super().__init__(graph)

    def _subgraph(self, edges=[], nodes=[],new_graph=None):
        return ViewGraph(super()._subgraph(edges,nodes,new_graph))
        
    def build(self,predicate="ALL"):
        edges = self._graph.edges(predicate=predicate)
        return self._subgraph(edges)