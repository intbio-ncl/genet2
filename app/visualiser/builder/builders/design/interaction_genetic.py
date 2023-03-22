from app.visualiser.builder.builders.design.interaction import AbstractViewBuilder
from app.visualiser.viewgraph.viewgraph import ViewGraph
from app.visualiser.builder.builders.design.utility import produce_aggregated_interaction_graph
from app.visualiser.builder.builders.design.utility import produce_interaction_graph
from  app.graph.utility.model.model import model

class InteractionGeneticViewBuilder(AbstractViewBuilder):
    def __init__(self,graph):
        super().__init__(graph)

    def _subgraph(self, new_graph):
        return ViewGraph(super()._subgraph(new_graph=new_graph))

    def build(self,predicate="ALL"):
        genetic_pred = model.identifiers.objects.DNA
        g = self._subgraph(produce_interaction_graph(self._graph,predicate=predicate))
        g = produce_aggregated_interaction_graph(g,genetic_pred)
        g = self._subgraph(g)
        g.remove_isolated_nodes()
        return g

