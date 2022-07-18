from app.visualiser.viewgraph.viewgraph import ViewGraph 
from app.visualiser.builder.abstract import AbstractBuilder

class TruthBuilder(AbstractBuilder):
    def __init__(self,graph):
        super().__init__(graph)
        self._dg = self._graph.get_design(None)
