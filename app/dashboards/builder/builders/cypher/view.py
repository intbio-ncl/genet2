from app.dashboards.builder.builders.abstract_view import AbstractViewBuilder
from app.graphs.graph_objects.node import Node
from app.graphs.graph_objects.edge import Edge

class ViewBuilder(AbstractViewBuilder):
    def __init__(self, builder):
        super().__init__(builder)

    def produce(self,qry_str,create_datatable):
        edges = []
        datatable = []
        elements = self._builder.run_query(qry_str)
        felements = [i for sl in elements for i in sl.values()]
        for record in elements:
            row = {}
            for qry_num,element in record.items():
                if isinstance(element,Node):
                    row[qry_num] = str(element)
                    r_edges = self._builder.get_edges(element)
                    for edge in r_edges:
                        if edge.v in felements:
                            edge.n = element
                            edge.v = [e for e in felements if edge.v == e][0]
                            edges.append(edge)
                elif isinstance(element,Edge):
                    edges.append(element)
                    row[qry_num] = str(element)
                else:
                    row[qry_num] = element 
            datatable.append(row)
        if create_datatable:
            return self._builder.sub_graph(edges),datatable
        return self._builder.sub_graph(edges)

        

