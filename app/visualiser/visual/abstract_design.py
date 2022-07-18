import os

import dash_cytoscape as cyto
cyto.load_extra_layouts()
from app.visualiser.visual.abstract import AbstractVisual
from app.visualiser.visual.handlers.design.layout import LayoutHandler
from app.visualiser.visual.handlers.design.label import LabelHandler
from app.visualiser.visual.handlers.design.color import ColorHandler
from app.visualiser.visual.handlers.design.size import SizeHandler
from app.visualiser.visual.handlers.design.shape import ShapeHandler

default_stylesheet_fn = os.path.join(os.path.dirname(os.path.realpath(__file__)),"default_stylesheet.txt")

class AbstractDesignVisual(AbstractVisual):
    def __init__(self,builder):
        super().__init__()
        self.view = self.set_full_graph_view
        self._builder = builder
        self._layout_h = LayoutHandler()
        self._label_h = LabelHandler(self._builder)
        self._color_h = ColorHandler(self._builder)
        self._size_h = SizeHandler(self._builder)
        self._shape_h = ShapeHandler(self._builder)
        self.set_concentric_layout()

    def get_design_names(self):
        return self._builder.get_design_names()
    
    def get_load_predicates(self):
        return self._builder.get_load_predicates()

    def set_design_names(self,names,load_predicate):
        self._builder.set_design_names(names,load_predicate)
        
    # ---------------------- View ---------------------    
    def set_pruned_view(self):
        '''
        Sub graph viewing the raw graph with specific edges removed 
        that are deemed not useful for visualisation.
        '''
        if self.view == self.set_pruned_view:
            self._builder.set_pruned_view()
        else:
           self.view =self.set_pruned_view

    def set_interaction_verbose_view(self):
        '''
        Sub graph viewing all interactions within the graph 
        including explicit inputs and outputs.
        '''
        if self.view == self.set_interaction_verbose_view:
            self._builder.set_interaction_verbose_view()
        else:
           self.view =self.set_interaction_verbose_view

    def set_interaction_view(self):
        '''
        Sub graph viewing all interactions within the graph implicitly visualises 
        participants by merging interaction node and participant edges into a single edge. 
        '''
        if self.view == self.set_interaction_view:
            self._builder.set_interaction_view()
        else:
           self.view =self.set_interaction_view
        self._builder.set_interaction_view()

    def set_interaction_genetic_view(self):
        '''
        Sub graph viewing genetic interactions within the graph.
        Abstracts proteins and non-genetic actors.
        '''
        if self.view == self.set_interaction_genetic_view:
            self._builder.set_interaction_genetic_view()
        else:
           self.view =self.set_interaction_genetic_view

    def set_interaction_protein_view(self):
        '''
        Sub graph viewing interactions between proteins. Abstracts DNA + Non-genetic actors. 
        Only visulises what the effect the presence of a protein has upon other proteins.
        '''
        if self.view == self.set_interaction_protein_view:
            self._builder.set_interaction_protein_view()
        else:
           self.view =self.set_interaction_protein_view

    def set_hierarchy_view(self):
        '''
        Sub graph viewing the design as a heirachy of entities.
        '''
        if self.view == self.set_hierarchy_view:
            self._builder.set_hierarchy_view()
        else:
            self.view = self.set_hierarchy_view

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

