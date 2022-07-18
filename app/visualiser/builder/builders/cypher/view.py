from app.visualiser.builder.builders.abstract_view import AbstractViewBuilder
from app.visualiser.viewgraph.viewgraph import ViewGraph
from app.graph.utility.graph_objects.node import Node
from app.graph.utility.graph_objects.edge import Edge

class CypherViewBuilder(AbstractViewBuilder):
    def __init__(self,graph):
        super().__init__(graph)
        self.driver = graph.driver

    def _subgraph(self, edges=[],nodes=[], new_graph=None):
        return ViewGraph(super()._subgraph(edges,nodes,new_graph))

    def build(self,qry_str,create_datatable=True):
        edges = []
        datatable = []
        elements = self.driver.run_query(qry_str)
        felements = [i for sl in elements for i in sl.values()]
        for record in elements:
            row = {}
            for qry_num,element in record.items():
                if isinstance(element,Node):
                    row[qry_num] = str(element)
                    r_edges = self.driver.edge_query(element)
                    for edge in r_edges:
                        if edge.v in felements:
                            edge.n = element
                            edge.v = [e for e in felements if edge.v == e][0]
                            edges.append(edge)
                elif isinstance(element,Edge):
                    edges.append(element)
                    row[qry_num] = str(element)
                else:
                    row[qry_num] = str(element) 
            datatable.append(row)
        if create_datatable:
            return self._subgraph(edges),datatable
        return self._subgraph(edges)

    def get_edge_types(self):
        pass
    
    def get_node_types(self):
        pass

    def transform(self,edges):
        return []
        


        

