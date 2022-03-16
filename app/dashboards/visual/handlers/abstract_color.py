import re

from visual.handlers.color_producer import ColorPicker

color_picker = ColorPicker()
class AbstractNodeColorHandler:
    def __init__(self,builder):
        self._builder = builder
        self._color_picker = color_picker
    
    def standard(self):
        return [{"standard" : self._color_picker[0]} for node in self._builder.v_nodes()]

    def rdf_type(self):
        colors = []
        for node,data in self._builder.v_nodes(data=True):
            if self._builder.get_rdf_type(node) is not None:
                color = {"rdf_type" : self._color_picker[0]}
            else:
                color = {"no_type" : self._color_picker[1]}
            colors.append(color)
        return colors

    def graph_number(self):
        return [{f'{data["graph_number"]}' : self._color_picker[data["graph_number"]]} for node,data in self._builder.v_nodes(data=True)]
    
class AbstractEdgeColorHandler:
    def __init__(self,builder):
        self._builder = builder
        self._color_picker = color_picker

    def standard(self):
        return [{"standard" : "#888"} for e in self._builder.v_edges]
    
    def nv_type(self):
        colors = []
        col_map = {}
        col_index = 0
        for n,v,k in self._builder.v_edges(keys=True):
            if k not in col_map.keys():
                col_map[k] = self._color_picker[col_index]
                col_index +=1
            colors.append({_get_name(k):col_map[k]})
        return colors
    
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