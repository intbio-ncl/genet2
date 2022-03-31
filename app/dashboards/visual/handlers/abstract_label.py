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
            names.append("-".join([_get_name(l) for l in node.get_labels()]))
        return names

    def class_type(self):
        node_text = []
        for node in self._builder.v_nodes():
            props = node.get_properties()
            n_type = self._builder.get_rdf_type(node)
            if n_type != []:
                node_text.append("-".join([_get_name(n) for n in n_type[0].v.get_labels()]))
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
            names.append("-".join([l for l in node.get_labels()]))
        return names

class AbstractEdgeLabelHandler:
    def __init__(self,builder):
        self._builder = builder
        
    def none(self):
        return [None] * len([*self._builder.v_edges()])

    def name(self):
        edge_names = []
        for edge in self._builder.v_edges():
            edge_names.append("-".join([_get_name(e) for e in edge.get_labels()]))
        return edge_names

    def uri(self):
        names = []
        for node in self._builder.v_edges():
            names.append("-".join([l for l in node.get_labels()]))
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