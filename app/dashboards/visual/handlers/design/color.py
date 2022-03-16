import re
from visual.handlers.abstract_color import AbstractNodeColorHandler
from visual.handlers.abstract_color import AbstractEdgeColorHandler

class ColorHandler():
    def __init__(self,builder):
        self.node = self.NodeColorHandler(builder)
        self.edge = self.EdgeColorHandler(builder)

    class NodeColorHandler(AbstractNodeColorHandler):
        def __init__(self,builder):
            super().__init__(builder)
        
        def type(self):
            colors = []
            col_map = {None : {"No_Role" : self._color_picker[0]}}
            col_index = len(col_map)
            for n in self._builder.v_nodes():
                rdf_type = self._builder.get_rdf_type(n)
                if rdf_type is None:
                    colors.append(col_map[None])
                else:
                    name = _get_name(rdf_type[1]["key"])
                    if name not in col_map.keys():
                        col_map[name] = self._color_picker[col_index]
                        col_index += 1
                    colors.append({name : col_map[name]})
            return colors

        def role(self):
            '''
            Overview:
            The first layer of non-abstract classes 
            (Reaction,Interaction,DNA etc) are given a color.
            Each derived class within the design is given a 
            shade of that color.
            Why this looks so complicated is because we need 
            to find the last shade of that color used.
            '''
            colors = []
            col_map = {None : {"No_Role" : self._color_picker[0]}}
            shade_map = {}
            col_index = len(col_map)

            mg = self._builder._model_graph
            pe_id = mg.identifiers.objects.physical_entity
            c_id = mg.identifiers.objects.conceptual_entity
            pe_code = mg.get_class_code(pe_id)
            c_code = mg.get_class_code(c_id)
            pe_derived = [d[1]["key"] for d in mg.get_child_classes([pe_code,c_code])]
            for d in pe_derived:
                name = _get_name(d)
                col_map[name] = self._color_picker[col_index]
                col_index += 1
            for n in self._builder.v_nodes():
                n_type = self._builder.get_rdf_type(n)
                if n_type is None:
                    colors.append(col_map[None])
                    continue
                n_type = n_type[1]["key"]
                name = _get_name(n_type)
                if name not in col_map.keys():
                    n_t_code = mg.get_class_code(n_type)
                    for b in [i[1]["key"] for i in mg.get_bases(n_t_code)]:
                        if b in pe_derived:
                            base = b
                            p_col = col_map[_get_name(b)]
                            break
                    else:
                        colors.append(col_map[None])
                        continue
                    if base not in shade_map.keys():
                        shade_map[base] = p_col
                    p_col = shade_map[base]
                    shade = self._color_picker.increase_shade(p_col)
                    shade_map[base] = shade
                    col_map[name] = shade
                colors.append({name : col_map[name]})
            return colors

        def hierarchy(self):
            colors = []
            colors_map = _init_hierarchy_map(self)
            for n,data in self._builder.v_nodes(data=True):
                key = data["key"]
                if key not in colors_map.keys():
                    for o in [c[0] for c in self._builder.in_edges(n)]:
                        o = self._builder.nodes[o]["key"]
                        if o in colors_map.keys():
                            color,depth = colors_map[o]
                            colors.append({depth : color})
                            break
                    else:
                        colors.append({"Non-Hierarchical" : colors_map[None]})
                else:
                    color,depth = colors_map[key]
                    colors.append({depth : color})
            return colors

    class EdgeColorHandler(AbstractEdgeColorHandler):
        def __init__(self,builder):
            super().__init__(builder)
                
        def hierarchy(self):
            colors = []
            color_map = _init_hierarchy_map(self)
            for n,v,k in self._builder.v_edges(keys=True):
                n_data = self._builder.v_nodes[n]
                key = n_data["key"]
                if key not in color_map.keys():
                    for o in [c[0] for c in self._builder.in_edges(n)]:
                        o = self._builder.nodes[o]["key"]
                        if o in color_map.keys():
                            color,depth = color_map[o]
                            colors.append({f'Depth-{depth}' : color})
                            break
                    else:
                        colors.append({"Non-Hierarchical" : color_map[None]})
                else:
                    color,depth = color_map[key]
                    colors.append({f"Depth-{depth}" : color})
            return colors

def _init_hierarchy_map(handler):
    # Currently root is only one node but 
    # future proofing just in case.
    root_index = 0
    colors_map = {None : handler._color_picker[0]}
    true_root = None
    def _handle_branch(root_node,cur_col,cur_depth):
        child_color = handler._color_picker.increase_shade(cur_col)
        cur_depth +=1
        for child,data in [c[0] for c in handler._builder.get_children(root_node)]:
            depth_str = f'{_get_name(true_root)}-Depth-{cur_depth}'
            colors_map[data["key"]] = (child_color,depth_str)
            _handle_branch(child,child_color,cur_depth)

    for rn,data in handler._builder.get_root_entities():
        root_index +=1
        true_root = data["key"]
        depth_str = f'{_get_name(true_root)}-Depth-0'
        colors_map[true_root] = handler._color_picker[root_index],depth_str
        root_color = handler._color_picker[root_index]
        _handle_branch(rn,root_color,0)
    return colors_map

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