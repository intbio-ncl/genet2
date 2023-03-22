import re

from rdflib import URIRef,RDF

from app.graph.utility.model.model import model
from app.graph.utility.graph_objects.node import Node

def build_interaction_uri(n,v,e):
    def _cast_node(node):
        if isinstance(node,dict):
            node_str = "_".join(_get_name(str(val)) for val in node.values())
            namespace = _get_namespace(list(n.values())[0])
        elif isinstance(node,list):
            node_str = "_".join(_get_name(str(val)) for val in node)
            namespace = _get_namespace(n[0])
        elif isinstance(node,Node):
            node_str = _get_name(node.get_key())
            namespace = _get_namespace(n)
        else:
            node_str = _get_name(node)
            namespace = _get_namespace(node)
        return node_str,namespace

    n_str,namespace = _cast_node(n)
    v_str,_ = _cast_node(v)
    e_str = _get_name(e)
    return f'{namespace}/{n_str}_{e_str}_{v_str}/1'

def build_properties(uri,name):
    return {"name" : _get_name(uri),
            "graph_name" : name}

def create_consists_of(node,name):
    # Get restrictions from ontology for a given interaction.
    edges = []
    key = node.get_key()
    n_type = node.get_type()
    for restriction in model.get_restrictions_on(model.get_class_code(URIRef(n_type))):
        predicate, constraints = model.get_constraint(restriction)
        node_key = key + "/" + _get_name(n_type) + "/0"
        cur_node = Node(node_key,**build_properties(node_key,name))
        edges.append((node,cur_node,predicate,build_properties(predicate,name)))
        for index, (pred, element) in enumerate(constraints):
            e, e_data = element
            e_key = e_data["key"]
            r_node = _build_restriction_obj(key, e_key,name)
            if index == len(constraints) - 1:
                next_node = Node(RDF.nil,**build_properties(RDF.nil,name))  
            else:
                nk = key + "/" + _get_name(n_type) + "/" + str(index+1)
                next_node = Node(nk,**build_properties(nk,name))
            edges.append((cur_node, r_node,RDF.first,build_properties(RDF.first,name)))
            edges.append((cur_node, next_node,RDF.rest,build_properties(RDF.rest,name)))
            cur_node = next_node
    return edges

def _build_restriction_obj(parent, value,g_name):
    if parent[-1].isdigit:
        parent = parent[:-1]
    name = parent + "/" + _get_name(value)
    return Node(name, value,**build_properties(name,g_name))

def _get_namespace(n):
    n = n.get_key()
    return n.split(_get_name(n))[0]

def _get_name(subject):
    split_subject = _split(subject)
    if len(split_subject[-1]) == 1 and split_subject[-1].isdigit():
        return split_subject[-2]
    elif len(split_subject[-1]) == 3 and _isfloat(split_subject[-1]):
        return split_subject[-2]
    else:
        return split_subject[-1]

def _split(uri):
    return re.split('#|\/|:', uri)

def _isfloat(x):
    try:
        float(x)
        return True
    except ValueError:
        return False