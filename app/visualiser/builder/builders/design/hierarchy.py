from app.visualiser.builder.builders.abstract_view import AbstractViewBuilder
from app.visualiser.viewgraph.viewgraph import ViewGraph

class HierarchyViewBuilder(AbstractViewBuilder):
    def __init__(self,graph):
        super().__init__(graph)

    def _subgraph(self, edges=[], nodes=[],new_graph=None):
        return ViewGraph(super()._subgraph(edges,nodes,new_graph))

    def build(self,predicate="ALL"):
        edges = []
        for entity in self._graph.get_entity(predicate=predicate):
            children = self._graph.get_children(entity,predicate=predicate)
            if len(children) == 0:
                continue
            for child in children:
                edges.append(child)
        return self._subgraph(edges)


