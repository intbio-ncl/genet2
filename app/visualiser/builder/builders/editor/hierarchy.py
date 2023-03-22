from app.visualiser.builder.builders.design.hierarchy import HierarchyViewBuilder
from  app.graph.utility.model.model import model
from app.visualiser.builder.builders.editor.common_builds import build_properties
class EditorHierarchyViewBuilder(HierarchyViewBuilder):
    def __init__(self,graph):
        super().__init__(graph)

    def build(self,predicate="ALL"):
        edges = []
        nodes = []
        for entity in self._graph.get_dna(predicate=predicate):
            children = self._graph.get_children(entity,predicate=predicate)
            if len(children) == 0:
                nodes.append(entity)
                continue
            for child in children:
                edges.append(child)
        return self._subgraph(edges,nodes)

    def get_edge_types(self):
        return [str(model.identifiers.predicates.has_part)]
    
    def get_node_types(self):
        c_id = model.get_class_code(model.identifiers.objects.physical_entity)
        return [str(k[1]["key"]) for k in model.get_derived(c_id)]

    def transform(self,n,v,e):
        v_edges = self.get_edge_types()
        v_nodes = self.get_node_types()
        edges = []
        if e not in v_edges:
            return []
        for node in n.values():
            if node.get_type() not in v_nodes:
                continue
            for vertex in v.values():
                if vertex.get_type() not in v_nodes:
                    continue
                edges.append((node,vertex,e,build_properties(e,self._graph.name)))
        return edges
