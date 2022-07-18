from app.visualiser.builder.abstract import AbstractBuilder
from app.visualiser.builder.builders.cypher.view import CypherViewBuilder

class CypherBuilder(AbstractBuilder):
    def __init__(self,graph):
        super().__init__(graph)
        self._dg = self._graph.get_design("*")
        self.qry_str = self.default_query()

    def default_query(self):
        return "MATCH (n) RETURN n LIMIT 25"
    
    def set_query(self,qry_str):
        self.qry_str = qry_str

    def build(self,create_datatable=True):
        view,dt = self._view_builder.build(self.qry_str,create_datatable)
        self.view=view
        return dt

    def set_cypher_view(self):
        self._view_builder = CypherViewBuilder(self._graph)

    def run_query(self,qry_str):
        return self._graph.run_query(qry_str)
    
    def get_edges(self,node):
        return self._graph.edge_query(n=node)