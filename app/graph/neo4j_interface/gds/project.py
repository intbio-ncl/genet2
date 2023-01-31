from app.graph.neo4j_interface.gds.query_builder import GDSQueryBuilder
from app.graph.utility.graph_objects.node import Node
class Projection():
    def __init__(self, interface):
        self._driver = interface.driver
        self._qry_builder = GDSQueryBuilder()
    
    def project(self, name, nodes, edges, **kwargs):
        nodes = [n.get_key() if isinstance(n,Node) else n for n in nodes ]
        return self._driver.graph.project(name, nodes, edges, **kwargs)
        
    def drop(self, name):
        g = self.get_graph(name)
        g.drop()

    def names(self):
        res = self._driver.graph.list()
        return (list(res["graphName"]))
        
    def get_graph(self, graph_name):
        return self._driver.graph.get(graph_name)

    def cypher_project(self, name, n, e):
        qry = self._qry_builder.cypher_project(name, n, e)
        ret = self._run(qry)
        return self.get_graph(name)
        
    def sub_graph(self, o_name, n_name, nodes, edges):
        qry = self._qry_builder.subgraph(o_name, n_name, nodes, edges)
        ret = self._run(qry)
        return self.get_graph(n_name)
        
    def mutate(self, name, types, mutate_type, node_labels=None):
        if node_labels and not isinstance(node_labels, list):
            node_labels = [str(node_labels)]
        qry = self._qry_builder.mutate(name, types, mutate_type, node_labels)
        print(qry)
        return self._run(qry)
        
    def _run(self,qry):
        return self._driver.run_cypher(qry)