from app.visualiser.builder.builders.abstract_view import AbstractViewBuilder
from app.visualiser.viewgraph.viewgraph import ViewGraph
from app.graph.utility.graph_objects.edge import Edge

class InteractionExplicitViewBuilder(AbstractViewBuilder):
    def __init__(self,graph):
        super().__init__(graph)

    def _subgraph(self, edges=[], nodes=[],new_graph=None):
        return ViewGraph(super()._subgraph(edges,nodes,new_graph))

    def build(self,predicate="ALL"):
        edges = []
        for interaction in self._graph.get_interaction(predicate=predicate):
            consistsOf = self._graph.get_consistsof(interaction,predicate=predicate)
            if consistsOf == []:
                raise NotImplementedError("Not Implemented.")
            consistsOf = consistsOf[0]
            consistsOf = self._graph.resolve_list(consistsOf.v,predicate=predicate)
            inputs, outputs = self._graph.get_interaction_io(interaction,predicate=predicate)
            for index, n in enumerate(consistsOf):
                if index == len(consistsOf) - 1:
                    for obj_e in outputs:
                        edges.append(Edge(n.v,obj_e.v,obj_e.get_type(),**obj_e.get_properties()))
                if index == 0:
                    for obj_e in inputs:
                        edges.append(Edge(obj_e.v,n.v,obj_e.get_type(),**obj_e.get_properties()))
                    continue
                p_element = consistsOf[index-1].v
                edges.append(Edge(p_element,n.v,obj_e.get_type(),**obj_e.get_properties()))
        return self._subgraph(edges)