from app.visualiser.builder.builders.abstract_view import AbstractViewBuilder
from app.visualiser.viewgraph.projectgraph import ProjectGraph

class NoneViewBuilder(AbstractViewBuilder):
    def __init__(self,graph):
        super().__init__(graph)

    def _subgraph(self, edges=[],nodes=[], new_graph=None,project_graph=None):
        g = ProjectGraph(super()._subgraph(edges,nodes,new_graph))
        g.set_project(project_graph)
        return g
        
    def build(self, graph_name,datatable=False):
        if datatable:
            return self._subgraph([]),[]
        return self._subgraph([])

    def get_edge_types(self):
        pass
    
    def get_node_types(self):
        pass

    def transform(self,edges):
        return []