import re

# Note the two len() you could add a num_nodes func (Performance)
class AbstractNodeLabelHandler:
    def __init__(self,builder):
        self._builder = builder

    def none(self):
        return [None] * len([*self._builder.v_nodes()])
    
    def adjacency(self):
        node_text = []
        for node in self._builder.v_nodes():
            num_in = len([*self._builder.in_edges(node)])
            num_out = len([*self._builder.out_edges(node)])
            node_text.append(f"# IN: {str(num_in)}, # OUT: {str(num_out)}")
        return node_text

    def name(self):
        names = []
        for node in self._builder.v_nodes():
            names.append(node.name)
        return names

    def class_type(self):
        node_text = []
        for node in self._builder.v_nodes():
            props = node.get_properties()
            n_type = node.get_type()
            if n_type is not None:
                node_text.append(_get_name(n_type))
            elif props["type"] == "Literal":
                node_text.append("Literal")
            elif props["type"] == "URI":
                node_text.append("Identifier")
            else:
                node_text.append("?")
        return node_text
        
    def uri(self):
        names = []
        for node in self._builder.v_nodes():
            names.append(node.get_key())
        return names

class AbstractEdgeLabelHandler:
    def __init__(self,builder):
        self._builder = builder
        
    def none(self):
        return [None] * len([*self._builder.v_edges()])

    def name(self):
        edge_names = []
        for edge in self._builder.v_edges():
            edge_names.append(edge.name)
        return edge_names

    def uri(self):
        names = []
        for edge in self._builder.v_edges():
            names.append(edge.get_type())
        return names

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