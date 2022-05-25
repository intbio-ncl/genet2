from app.dashboards.builder.builders.abstract_view import AbstractViewBuilder
import re
class ViewBuilder(AbstractViewBuilder):
    def __init__(self, builder):
        super().__init__(builder)

    def none(self):
        return self._builder.sub_graph([])
        
    def projection(self, graph_name,datatable=False):
        p_graph = self._builder.get_project_graph(graph_name)
        graph = self._builder.build_projection_graph(p_graph)
        
        if not datatable:
            return graph
        datatable = []
        for edge in graph.edges():
            row = {"n" : str(edge.n.name),
                   "v" : str(edge.v.name),
                   "e" : str(edge.name)}
            datatable.append(row)
        return graph, datatable
