import networkx as nx
from app.graph.utility.graph_objects.edge import Edge
from app.graph.utility.model.model import model
from app.graph.utility.graph_objects.reserved_node import ReservedNode
from app.graph.utility.model.identifiers import  KnowledgeGraphIdentifiers
ids = KnowledgeGraphIdentifiers()

def _get_conf(n,v):
    return {str(ids.external.confidence) : int((n.confidence + v.confidence)/2)}

def produce_interaction_graph(graph,predicate="ALL"):
    edges = []
    for interaction in graph.get_interaction(predicate=predicate):
        inputs, outputs = graph.get_interaction_io(interaction,predicate=predicate)
        if len(outputs) == 0:
            continue
        for inp in inputs:
            for out in outputs:
                if isinstance(interaction,ReservedNode):
                    interaction.update(_get_conf(inp,out))
                edges.append(Edge(inp.v, out.v, interaction.get_type(),**interaction.get_properties()))
    return _subgraph(edges)

def produce_aggregated_interaction_graph(i_graph, i_type, first_pred=False):
    edges = []
    g_code = [model.get_class_code(i_type)]
    for node in i_graph.nodes():
        n_type = node.get_type()
        if n_type == "None":
            continue
        if not model.is_derived(n_type, g_code):
            continue
        for e in find_nearest_interaction(node, g_code, i_graph, first_pred):
            edges.append(Edge(node,e.v,e.get_type(),**e.get_properties()))
    return _subgraph(edges)

def find_nearest_interaction(node, target_types, i_graph, use_first=False):
    def _find_nearest_inner(c_node, index=0, first_pred=None):
        i_targets = []
        for edge in i_graph.edges(c_node):
            # Self Loops.
            if edge.n == edge.v:
                continue
            if index == 0:
                first_pred = edge.get_type()
            node_type = edge.v.get_type()
            if node_type == "None":
                continue
            if model.is_derived(node_type, target_types):
                if use_first:
                    e = first_pred
                i_targets.append((edge,index))
                continue
            i_targets += _find_nearest_inner(edge.v, index+1, first_pred)
        return i_targets

    targets = _find_nearest_inner(node)
    f_targets = []
    # Remove paths to same object (Remove longest.)
    if len(targets) < 2:
        return [t[0] for t in targets]
    for index1, (edge,distance1) in enumerate(targets):
        if [t[0].v for t in targets].count(edge.v) == 1:
            f_targets.append(edge)
            continue
        for index2, (edge2,distance2) in enumerate(targets):
            if index1 == index2:
                continue
            if edge.v != edge2.v:
                continue
            if distance2 > distance1:
                f_targets.append(edge)
            elif distance1 > distance2:
                f_targets.append(edge2)
            else:
                f_targets.append(edge)
                f_targets.append(edge2)
    return f_targets

def _subgraph(edges=[], new_graph=None):
    if not new_graph:
        new_graph = nx.MultiDiGraph()
        for e in edges:
            n = e.n
            v = e.v
            e_key = e.get_type()
            new_graph.add_node(n.id,key=n.get_key(),type=n.get_type(),**n.get_properties())
            new_graph.add_node(v.id,key=v.get_key(),type=v.get_type(),**v.get_properties())
            new_graph.add_edge(n.id,v.id,e_key,**e.get_properties())
    return new_graph