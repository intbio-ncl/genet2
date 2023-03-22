import os

import dash_cytoscape as cyto
cyto.load_extra_layouts()
from app.visualiser.builder.truth import TruthBuilder
from app.visualiser.visual.abstract import AbstractVisual
from app.visualiser.visual.handlers.truth.layout import TruthLayoutHandler
from app.visualiser.visual.handlers.truth.label import TruthLabelHandler
from app.visualiser.visual.handlers.truth.color import TruthColorHandler
from app.visualiser.visual.handlers.truth.size import TruthSizeHandler
from app.visualiser.visual.handlers.truth.shape import TruthShapeHandler

default_stylesheet_fn = os.path.join(os.path.dirname(os.path.realpath(__file__)),"default_stylesheet.txt")

class TruthVisual(AbstractVisual):
    def __init__(self,graph):
        super().__init__()
        self.view = self.set_full_graph_view
        self._builder = TruthBuilder(graph)
        self._layout_h = TruthLayoutHandler()
        self._label_h = TruthLabelHandler(self._builder)
        self._color_h = TruthColorHandler(self._builder)
        self._size_h = TruthSizeHandler(self._builder)
        self._shape_h = TruthShapeHandler(self._builder)
        self.set_concentric_layout()
            
    # ---------------------- Preset ------------------------------------
    def set_hierarchy_preset(self):
        '''
        Pre-set methods with an affinity for displaying the hierarchy view.
        '''
        preset_functions = [self.set_tree_mode,
                            self.set_hierarchy_view,
                            self.set_dagre_layout,
                            self.add_hierarchy_node_color,
                            self.add_hierarchy_edge_color,
                            self.add_node_name_labels, 
                            self.add_edge_no_labels,
                            self.add_hierarchy_node_size,
                            self.set_circle_node_shape,
                            self.set_bezier_edge_shape]
        return self._set_preset(preset_functions)

    def set_prune_preset(self):
        '''
        Pre-set methods with an affinity for displaying the pruned graph view.
        '''
        preset_functions = [self.set_network_mode,
                            self.set_pruned_view,
                            self.set_cose_layout,
                            self.add_type_node_color, 
                            self.add_type_edge_color,
                            self.add_node_name_labels,
                            self.add_edge_no_labels,
                            self.add_centrality_node_size,
                            self.set_circle_node_shape,
                            self.set_bezier_edge_shape]
        return self._set_preset(preset_functions)

    def set_interaction_level_1_verbose_preset(self):
        '''
        Pre-set methods with an affinity for displaying the verbose interaction view.
        '''
        preset_functions = [self.set_network_mode,
                            self.set_interaction_verbose_view,
                            self.set_dagre_layout,
                            self.add_role_node_color,
                            self.add_type_edge_color,
                            self.add_edge_no_labels,
                            self.add_node_name_labels,
                            self.add_standard_node_size,
                            self.set_circle_node_shape,
                            self.set_bezier_edge_shape]
        return self._set_preset(preset_functions)

    def set_interaction_level_2_standard_preset(self):
        '''
        Pre-set methods with an affinity for displaying the interaction view.
        '''
        preset_functions = [self.set_network_mode,
                            self.set_interaction_view,
                            self.set_dagre_layout,
                            self.add_role_node_color,
                            self.add_type_edge_color,
                            self.add_edge_no_labels,
                            self.add_node_name_labels,
                            self.add_standard_node_size,
                            self.set_circle_node_shape,
                            self.set_bezier_edge_shape]
        return self._set_preset(preset_functions)

    def set_interaction_level_3_genetic_preset(self):
        '''
        Pre-set methods with an affinity for displaying the genetic interaction view.
        '''
        preset_functions = [self.set_network_mode,
                            self.set_interaction_genetic_view,
                            self.set_dagre_layout,
                            self.add_type_node_color,
                            self.add_type_edge_color,   
                            self.add_edge_no_labels,
                            self.add_node_name_labels,
                            self.add_standard_node_size,
                            self.set_circle_node_shape,
                            self.set_bezier_edge_shape]
        return self._set_preset(preset_functions)

    def set_interaction_level_4_protein_preset(self):
        '''
        Pre-set methods with an affinity for displaying the ppi interaction view.
        '''
        preset_functions = [self.set_network_mode,
                            self.set_interaction_protein_view,
                            self.set_dagre_layout,
                            self.add_type_edge_color,
                            self.add_type_node_color,
                            self.add_node_name_labels,
                            self.add_edge_no_labels,
                            self.add_standard_node_size,
                            self.set_circle_node_shape,
                            self.set_bezier_edge_shape]
        return self._set_preset(preset_functions)


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

    def add_confidence_edge_color(self):
        '''
        Confidence is mapped to a color.
        '''
        if self.edge_color == self.add_confidence_edge_color:
            return self._color_h.edge.confidence()
        else:
            self.edge_color = self.add_confidence_edge_color

    # ---------------------- Node Size ----------------------
    def add_hierarchy_node_size(self):
        '''
        The lower a node in the graph as a heirachy the smaller the node.
        '''
        if self.node_size == self.add_hierarchy_node_size:
            return self._size_h.hierarchy()
        else:
            self.node_size = self.add_hierarchy_node_size


    def add_edge_confidence_labels(self):
        '''
        Truth edge confidence is presented as labels.
        '''
        if self.edge_text == self.add_edge_confidence_labels:
            return self._label_h.edge.confidence()
        else:
            self.edge_text = self.add_edge_confidence_labels