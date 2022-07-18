from app.visualiser.builder.builders.abstract_view import AbstractViewBuilder
from app.visualiser.viewgraph.viewgraph import ViewGraph

class ViewBuilder(AbstractViewBuilder):
    def __init__(self,graph):
        super().__init__(graph)
    
    def _subgraph(self, edges=[], new_graph=None):
        return ViewGraph(super()._subgraph(edges,new_graph))

