from app.visualiser.builder.builders.abstract_view import AbstractViewBuilder
from app.visualiser.viewgraph.viewgraph import ViewGraph
from app.graph.utility.graph_objects.edge import Edge
from  app.graph.utility.model.model import model

pe = model.get_class_code(model.identifiers.objects.physical_entity)
interaction = model.get_class_code(model.identifiers.objects.interaction)
class InteractionVerboseViewBuilder(AbstractViewBuilder):
    def __init__(self,graph):
        super().__init__(graph)

    def _subgraph(self, edges=[], nodes=[],new_graph=None):
        return ViewGraph(super()._subgraph(edges,nodes,new_graph))

    def build(self):
        edges = []
        for interaction in self._graph.get_interaction():
            inputs, outputs = self._graph.get_interaction_io(interaction)
            for obj in inputs:
                edges.append((Edge(obj.v, interaction, obj.get_type(), **obj.get_properties())))
            for obj in outputs:
                edges.append((Edge(interaction,obj.v, obj.get_type(), **obj.get_properties())))
        return self._subgraph(edges)
