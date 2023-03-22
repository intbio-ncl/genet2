from app.visualiser.builder.builders.full import FullViewBuilder
from app.visualiser.viewgraph.viewgraph import ViewGraph
from  app.graph.utility.model.model import model
from app.visualiser.builder.builders.editor.common_builds import build_properties
class EditorFullViewBuilder(FullViewBuilder):
    def __init__(self,graph):
        super().__init__(graph)

    def build(self,predicate="ALL"):
        g = super().build(predicate=predicate)
        iso_nodes = self._graph.get_isolated_nodes(predicate=predicate)
        for node in iso_nodes:
            g.add_node(node)
        return g

    def get_edge_types(self):
        return [k[1]["key"] for k in model.get_properties()]
    
    def get_node_types(self):
        return [k[1]["key"] for k in model.get_classes(False)]
    
    def transform(self,n,v,e):
        edges = []
        for node in n.values():
            for vertex in v.values():
                edges.append((node,vertex,e,build_properties(e,self._graph.name)))
        return edges
