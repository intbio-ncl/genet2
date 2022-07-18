from app.visualiser.builder.builders.abstract_view import AbstractViewBuilder
from app.visualiser.viewgraph.viewgraph import ViewGraph
from app.visualiser.builder.builders.design.utility import produce_aggregated_interaction_graph
from app.visualiser.builder.builders.design.utility import produce_interaction_graph
from app.graph.utility.model.model import model


class InteractionProteinViewBuilder(AbstractViewBuilder):
    def __init__(self, graph):
        super().__init__(graph)

    def _subgraph(self, new_graph):
        return ViewGraph(super()._subgraph(new_graph=new_graph))

    def build(self):
        pp = model.identifiers.objects.protein
        g = self._subgraph(produce_interaction_graph(self._graph))
        g = produce_aggregated_interaction_graph(g, pp)
        g = self._subgraph(g)
        g.remove_isolated_nodes()
        return g


