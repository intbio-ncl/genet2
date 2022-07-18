import os

import dash_cytoscape as cyto
cyto.load_extra_layouts()
from app.visualiser.builder.truth import TruthBuilder
from app.visualiser.visual.abstract import AbstractVisual
from app.visualiser.visual.handlers.design.layout import LayoutHandler
from app.visualiser.visual.handlers.design.label import LabelHandler
from app.visualiser.visual.handlers.design.color import ColorHandler
from app.visualiser.visual.handlers.design.size import SizeHandler
from app.visualiser.visual.handlers.design.shape import ShapeHandler

default_stylesheet_fn = os.path.join(os.path.dirname(os.path.realpath(__file__)),"default_stylesheet.txt")

class TruthVisual(AbstractVisual):
    def __init__(self,graph):
        super().__init__()
        self.view = self.set_full_graph_view
        self._builder = TruthBuilder(graph)
        self._layout_h = LayoutHandler()
        self._label_h = LabelHandler(self._builder)
        self._color_h = ColorHandler(self._builder)
        self._size_h = SizeHandler(self._builder)
        self._shape_h = ShapeHandler(self._builder)
        self.set_concentric_layout()
            
    def add_type_node_color(self):
        '''
        Each Class is mapped to a distinct color.
        '''
        if self.node_color == self.add_type_node_color:
            return self._color_h.node.type()
        else:
            self.node_color = self.add_type_node_color

    def add_role_node_color(self):
        '''
        Each Physical Entity is given a color, 
        each derived class is a shade.
        '''
        if self.node_color == self.add_role_node_color:
            return self._color_h.node.role()
        else:
            self.node_color = self.add_role_node_color
    
    def add_hierarchy_node_color(self):
        '''
        Each Role is mapped to a distinct color.
        '''
        if self.node_color == self.add_hierarchy_node_color:
            return self._color_h.node.hierarchy()
        else:
            self.node_color = self.add_hierarchy_node_color

    # ---------------------- Edge Color ----------------------
    def add_hierarchy_edge_color(self):
        '''
        Each Role is mapped to a distinct color.
        '''
        if self.edge_color == self.add_hierarchy_edge_color:
            return self._color_h.edge.hierarchy()
        else:
            self.edge_color = self.add_hierarchy_edge_color

    # ---------------------- Node Size ----------------------
    def add_hierarchy_node_size(self):
        '''
        The lower a node in the graph as a heirachy the smaller the node.
        '''
        if self.node_size == self.add_hierarchy_node_size:
            return self._size_h.hierarchy()
        else:
            self.node_size = self.add_hierarchy_node_size

