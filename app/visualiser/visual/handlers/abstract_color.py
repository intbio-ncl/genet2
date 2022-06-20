import re

from app.visualiser.visual.handlers.color_producer import ColorPicker

color_picker = ColorPicker()
class AbstractNodeColorHandler:
    def __init__(self,builder):
        self._builder = builder
        self._color_picker = color_picker
    
    def standard(self):
        return [{"standard" : self._color_picker[0]} for node in self._builder.v_nodes()]

    def rdf_type(self):
        colors = []
        for node in self._builder.v_nodes():
            if node.get_type() != "None":
                color = {"rdf_type" : self._color_picker[0]}
            else:
                color = {"no_type" : self._color_picker[1]}
            colors.append(color)
        return colors

    def graph_name(self):
        colors = []
        seens = {}
        index = 0
        for node in self._builder.v_nodes():
            gn = frozenset(node["graph_name"])
            if gn in seens :
                color = seens[gn]
            else:
                color = self._color_picker[index]
                index += 1
                seens[gn] = color
            colors.append({"-".join(gn):color}  )
        return colors
    
class AbstractEdgeColorHandler:
    def __init__(self,builder):
        self._builder = builder
        self._color_picker = color_picker

    def standard(self):
        return [{"standard" : "#888"} for e in self._builder.v_edges()]
    
    def nv_type(self):
        colors = []
        col_map = {}
        col_index = 0
        for edge in self._builder.v_edges():
            edge = _get_name(edge.get_type())
            if edge not in col_map:
                col_map[edge] = self._color_picker[col_index]
                col_index +=1
            colors.append({edge:col_map[edge]})
        return colors

    def graph_name(self):
        colors = []
        seens = {}
        index = 0
        for edge in self._builder.v_edges():
            gn = frozenset(edge["graph_name"])
            if gn in seens :
                color = seens[gn]
            else:
                color = self._color_picker[index]
                index += 1
                seens[gn] = color
            colors.append({"-".join(gn):color}  )
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