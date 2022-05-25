import re

class AbstractNodeShapeHandler:
    def __init__(self,builder):
        self._builder = builder
        self.shapes = ["circle",
                    "square",
                    "triangle",
                    "rectangle",
                    "diamond",
                    "hexagon",
                    "octagon",
                    "vee",
                    "parallelogram",
                    "roundrect",
                    "ellipse"]
    
    def adaptive(self):
        default_shape = self.shapes[0]
        shapes = self.shapes[1:]
        node_shapes = []
        shape_map = {"no_type" : default_shape}
        counter = 0
        for node in self._builder.v_nodes():
            obj_type = node.get_type()
            if obj_type == "None":
                shape = shape_map["no_type"]
                obj_type = "No Type"
            else:
                obj_type = _get_name(node.get_type())
                if obj_type in shape_map.keys():
                    shape = shape_map[obj_type]
                else:
                    shape = shapes[counter]
                    shape_map[obj_type] = shape
                    if counter == len(shapes) - 1:
                        counter = 0
                    else:
                        counter = counter + 1 
            node_shapes.append({obj_type : shape})
        return node_shapes

    def circle(self):
        return [{"standard" : "circle"} for node in self._builder.v_nodes()]
        
    def square(self):
        return [{"standard" : "square"} for node in self._builder.v_nodes()]
        
    def triangle(self):
        return [{"standard" : "triangle"} for node in self._builder.v_nodes()]
        
    def rectangle(self):
        return [{"standard" : "rectangle"} for node in self._builder.v_nodes()]
        
    def diamond(self):
        return [{"standard" : "diamond"} for node in self._builder.v_nodes()]
        
    def hexagon(self):
        return [{"standard" : "hexagon"} for node in self._builder.v_nodes()]
        
    def octagon(self):
        return [{"standard" : "octagon"} for node in self._builder.v_nodes()]
        
    def vee(self):
        return [{"standard" : "vee"} for node in self._builder.v_nodes()]
        
class AbstractEdgeShapeHandler:
    def __init__(self):
        pass

    def straight(self):
        return "straight"
    def bezier(self):
        return "bezier"
    def taxi(self):
        return "taxi"
    def unbundled_bezier(self):
        return "unbundled_bezier"
    def loop(self):
        return "loop"
    def haystack(self):
        return "haystack"
    def segments(self):
        return "segments"

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