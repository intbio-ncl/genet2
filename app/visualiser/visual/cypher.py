import os

import dash_cytoscape as cyto
cyto.load_extra_layouts()
from app.visualiser.builder.cypher import CypherBuilder
from app.visualiser.visual.abstract import AbstractVisual
from app.visualiser.visual.handlers.design.layout import LayoutHandler
from app.visualiser.visual.handlers.design.label import LabelHandler
from app.visualiser.visual.handlers.design.color import ColorHandler
from app.visualiser.visual.handlers.design.size import SizeHandler
from app.visualiser.visual.handlers.design.shape import ShapeHandler

default_stylesheet_fn = os.path.join(os.path.dirname(os.path.realpath(__file__)),"default_stylesheet.txt")
 
class CypherVisual(AbstractVisual):
    def __init__(self,graph):
        super().__init__()
        self.view = self.set_cypher_view
        self._builder = CypherBuilder(graph)
        self._layout_h = LayoutHandler()
        self._label_h = LabelHandler(self._builder)
        self._color_h = ColorHandler(self._builder)
        self._size_h = SizeHandler(self._builder)
        self._shape_h = ShapeHandler(self._builder)
        self.set_concentric_layout()

    def set_default_preset(self):
        preset_functions = [self.set_network_mode,
                            self.set_cypher_view,
                            self.set_cola_layout,
                            self.add_standard_node_color,
                            self.add_standard_edge_color,
                            self.add_node_name_labels, 
                            self.add_edge_name_labels,
                            self.add_standard_node_size,
                            self.set_circle_node_shape,
                            self.set_bezier_edge_shape]
        return self._set_preset(preset_functions)
        
    def set_cypher_view(self):
        if self.view == self.set_cypher_view:
            return self._builder.set_cypher_view()
        else:
           self.view =self.set_cypher_view

    def default_query(self):
        return self._builder.default_query()

    def set_query(self,qry):
        return self._builder.set_query(qry)