from app.visualiser.builder.builders.design.interaction_verbose import InteractionVerboseViewBuilder
from app.visualiser.viewgraph.viewgraph import ViewGraph
from app.graph.utility.graph_objects.edge import Edge
from  app.graph.utility.model.model import model
from app.visualiser.builder.builders.editor.common_builds import build_properties

pe = model.get_class_code(model.identifiers.objects.physical_entity)
interaction = model.get_class_code(model.identifiers.objects.interaction)
class EditorInteractionVerboseViewBuilder(InteractionVerboseViewBuilder):
    def __init__(self,graph):
        super().__init__(graph)

    def build(self):
        edges = []
        nodes = []
        for interaction in self._graph.get_interaction():
            inputs, outputs = self._graph.get_interaction_io(interaction)
            for obj in inputs:
                edges.append((Edge(obj.v, interaction, obj.get_type(), **obj.get_properties())))
            for obj in outputs:
                edges.append((Edge(interaction,obj.v, obj.get_type(), **obj.get_properties())))
            nodes.append(interaction)
        return self._subgraph(edges,nodes)

    def get_edge_types(self):
        return [k[1]["key"] for k in model.interaction_predicates()]
    
    def get_node_types(self):
        return [k[1]["key"] for k in model.get_derived([pe,interaction])]

    def transform(self,n,v,e):
        et = [str(n) for n in self.get_edge_types()]
        pt = [str(k[1]["key"]) for k in model.get_derived(pe)]
        it  = [str(k[1]["key"]) for k in model.get_derived(interaction)]
        edges = []
        if e not in et:
            return []
        for node in n.values():
            if node.get_type() not in it:
                continue
            for vertex in v.values():
                if vertex.get_type() not in pt:
                    continue
                edges.append((node,vertex,e,build_properties(e,self._graph.name)))
        return edges