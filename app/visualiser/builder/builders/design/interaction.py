from app.visualiser.builder.builders.abstract_view import AbstractViewBuilder
from app.visualiser.viewgraph.viewgraph import ViewGraph
from app.visualiser.builder.builders.design.utility import produce_interaction_graph

class InteractionViewBuilder(AbstractViewBuilder):
    def __init__(self,graph):
        super().__init__(graph)

    def _subgraph(self, new_graph):
        return ViewGraph(super()._subgraph(new_graph=new_graph))

    def build(self):
        g = produce_interaction_graph(self._graph)
        return self._subgraph(g)