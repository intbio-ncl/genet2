

from app.visualiser.viewgraph.viewgraph import ViewGraph 
from app.visualiser.builder.abstract import AbstractBuilder
from app.visualiser.builder.builders.cypher.view import ViewBuilder
from app.visualiser.builder.builders.cypher.mode import ModeBuilder

class CypherBuilder(AbstractBuilder):
    def __init__(self,graph):
        super().__init__(graph)
        self._dg = self._graph.get_design("*")
        self.view = ViewGraph()
        self._view_h = ViewBuilder(self._graph)
        self._mode_h = ModeBuilder(self)

    def set_cypher_view(self,cypher_qry,datatable):
        if datatable:
            view,datatabe = self._view_h.produce(cypher_qry,datatable)
            self.view = view
            return datatabe
            
        self.view = self._view_h.produce(cypher_qry,datatable)

    def run_query(self,qry_str):
        return self._graph.run_query(qry_str)
    
    def get_edges(self,node):
        return self._graph.edge_query(n=node)