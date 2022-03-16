import re
from rdflib import URIRef,Literal,RDF

class AbstractNodeLabelHandler:
    def __init__(self,builder):
        self._builder = builder

    def none(self):
        return [None] * len(self._builder.v_nodes())
    
    def adjacency(self):
        node_text = []
        for node in self._builder.v_nodes:
            num_in = len(self._builder.in_edges(node))
            num_out = len(self._builder.out_edges(node)) 
            node_text.append(f"# IN: {str(num_in)}, # OUT: {str(num_out)}")
        return node_text

    def name(self):
        names = []
        for node,data in self._builder.v_nodes(data=True):
            names.append(data["display_name"])
        return names

    def class_type(self):
        node_text = []
        for node,data in self._builder.v_nodes(data=True):
            key = data["key"]
            n_type = self._builder.get_rdf_type(node)
            if n_type is not None:
                node_text.append(_get_name(n_type[1]["key"]))
            elif isinstance(key,Literal):
                node_text.append("Literal")
            elif isinstance(key,URIRef):
                node_text.append("Identifier")
            else:
                node_text.append("?")
        return node_text
        
    def uri(self):
        return [data["key"] for n,data in self._builder.v_nodes(data=True)]

class AbstractEdgeLabelHandler:
    def __init__(self,builder):
        self._builder = builder
        
    def none(self):
        return [None] * len(self._builder.v_edges())

    def name(self):
        edge_names = []
        for edge in self._builder.v_edges(data=True):
            edge_names.append(edge[2]["display_name"])
        return edge_names

    def uri(self):
        return [edge[2] for edge in self._builder.v_edges(keys=True)]

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