from rdflib import RDF
from app.visualiser.builder.builders.design.pruned import PrunedViewBuilder
from  app.graph.utility.model.model import model
from app.visualiser.viewgraph.viewgraph import ViewGraph
from app.visualiser.builder.builders.editor.common_builds import build_properties

bl_pred = {str(model.identifiers.predicates.consistsOf),str(RDF.type)}
w_predicates = list({str(p) for p in model.identifiers.predicates} - bl_pred)
                    

class EditorPrunedViewBuilder(PrunedViewBuilder):
    def __init__(self,graph):
        super().__init__(graph)

    def build(self,predicate="ALL"):
        edges = []
        for edge in self._graph.edges(predicate=predicate):
            if not edge.get_type() in w_predicates:
                continue
            edges.append(edge)
        return self._subgraph(edges,self._graph.get_isolated_nodes(predicate=predicate))

    def get_edge_types(self):
        return w_predicates
    
    def get_node_types(self):
        c_id = model.get_class_code(model.identifiers.objects.entity)
        return [k[1]["key"] for k in model.get_derived(c_id)]

    def transform(self,n,v,e):
        edges = []
        if e not in w_predicates:
            return []
        for node in n.values():
            for vertex in v.values():
                edges.append((node,vertex,e,build_properties(e,self._graph.name)))
        return edges

