from app.visualiser.builder.builders.abstract_view import AbstractViewBuilder
from app.visualiser.viewgraph.viewgraph import ViewGraph
from app.graph.utility.graph_objects.edge import Edge
from  app.graph.utility.model.model import model
from app.visualiser.builder.builders.design.utility import produce_interaction_graph
class InteractionIoViewBuilder(AbstractViewBuilder):
    def __init__(self,graph):
        super().__init__(graph)

    def build(self):
        edges = []
        i_graph = self._subgraph(new_graph=produce_interaction_graph(self._graph))
        genetic_pred = model.identifiers.objects.DNA
        d_pred = model.identifiers.predicates.direction
        inputs = []
        for n in i_graph.nodes():
            if len([*i_graph.in_edges(n)]) > 0:
                continue
            i_type = n.get_type()
            if i_type == genetic_pred or model.is_derived(i_type,genetic_pred):
                continue
            inputs.append(n)
        for inp in inputs:
            dfs = list(i_graph.bfs(inp))
            for (n, v) in dfs:
                i_type = v.get_type()
                if i_type == genetic_pred or model.is_derived(i_type,genetic_pred):
                    continue
                if [d[0] for d in dfs].count(v) == 0:
                    edges.append(Edge(inp,v,d_pred))
        return self._subgraph(edges)