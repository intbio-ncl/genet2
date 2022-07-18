import dash_cytoscape as cyto
cyto.load_extra_layouts()
from app.visualiser.visual.abstract_design import AbstractDesignVisual
from app.visualiser.builder.design import DesignBuilder

class DesignVisual(AbstractDesignVisual):
    def __init__(self,graph):
        super().__init__(DesignBuilder(graph))

        
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

    def set_interaction_level_0_explicit_preset(self):
        '''
        Pre-set methods with an affinity for displaying the explicit interaction view.
        '''
        preset_functions = [self.set_network_mode,
                            self.set_interaction_explicit_view,
                            self.set_dagre_layout,
                            self.add_role_node_color,
                            self.add_type_edge_color,
                            self.add_edge_no_labels,
                            self.add_node_name_labels,
                            self.add_standard_node_size,
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

    def set_interaction_level_5_io_preset(self):
        '''
        Pre-set methods with an affinity for displaying the ppi interaction view.
        '''
        preset_functions = [self.set_network_mode,
                            self.set_interaction_io_view,
                            self.set_dagre_layout,
                            self.add_type_edge_color,
                            self.add_standard_node_color,
                            self.add_node_name_labels,
                            self.add_edge_no_labels,
                            self.add_standard_node_size,
                            self.set_circle_node_shape,
                            self.set_bezier_edge_shape]
        return self._set_preset(preset_functions)


    def set_interaction_explicit_view(self):
        '''
        Sub graph viewing all consituent reactions of each interaction. 
        '''
        if self.view == self.set_interaction_explicit_view:
            self._builder.set_interaction_explicit_view()
        else:
           self.view =self.set_interaction_explicit_view

    def set_interaction_io_view(self):
        '''
        Sub graph viewing inputs and outputs of interaction network only.
        '''
        if self.view == self.set_interaction_io_view:
            self._builder.set_interaction_io_view()
        else:
           self.view =self.set_interaction_io_view