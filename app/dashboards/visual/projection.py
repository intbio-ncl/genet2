import os
from typing import final
import dash_cytoscape as cyto
cyto.load_extra_layouts()
from app.dashboards.builder.projection import ProjectionBuilder
from app.dashboards.visual.abstract import AbstractVisual
from app.dashboards.visual.handlers.design.layout import LayoutHandler
from app.dashboards.visual.handlers.design.label import LabelHandler
from app.dashboards.visual.handlers.design.color import ColorHandler
from app.dashboards.visual.handlers.design.size import SizeHandler
from app.dashboards.visual.handlers.design.shape import ShapeHandler

default_stylesheet_fn = os.path.join(os.path.dirname(os.path.realpath(__file__)),"default_stylesheet.txt")
 
class ProjectionVisual(AbstractVisual):
    def __init__(self,graph):
        super().__init__()
        self.view = self.set_no_view
        self._builder = ProjectionBuilder(graph)
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
            
    def set_no_view(self,datatable=False):
        if self.view == self.set_no_view:
            return self._builder.set_no_view()
        else:
           self.view =self.set_no_view
    
    def set_projection_view(self,datatable=False):
        if self.view == self.set_projection_view:
            return self._builder.set_projection_view(self.projection_name,datatable)
        else:
           self.view =self.set_projection_view

    def get_project_preset_names(self):
        return self._builder.get_project_preset_names()
        
    def get_project_graph_names(self):
        return self._builder.get_project_graph_names()

    def set_projection_graph(self,graph_name):
        self.projection_name = graph_name
    
    def run_cypher(self,cypher_str):
        return self._builder.run_query(cypher_str)

    def project_graph(self,name,nodes,edges,n_props,e_props,**kwargs):
        return self._builder.project_graph(name,nodes,edges,n_props,e_props,**kwargs)
    
    def project_preset(self,name,preset):
        return self._builder.project_preset(name,preset)
    
    def get_node_labels(self):
        return self._builder.get_node_labels()
        
    def get_edge_labels(self):
        return self._builder.get_edge_labels()

    def get_node_properties(self):
        return self._builder.get_node_properties()

    def get_edge_properties(self):
        return self._builder.get_edge_properties()

    def get_node_property_names(self):
        res = self._builder.get_node_properties().values
        return (list(set([item for sublist in res for item in sublist.keys()])))

    def get_edge_property_names(self):
        res = self._builder.get_edge_properties().values
        return (list(set([item for sublist in res for item in sublist.keys()])))

    def get_graph_metadata(self):
        return self._builder.get_graph_metadata()
    
    def get_project_info(self):
        return self._builder.get_project_info()
    
    def get_procedures_info(self):
        return self._builder.get_procedures_info()

    def get_parameter_types(self,params):
        return self._builder.get_parameter_types(params)
    
    def run_procedure(self,module,name,params):
        final_elements = []
        def iterdict(d):
                for k, v in d.items():
                    if isinstance(v, dict):
                        iterdict(v)
                    else:
                        if not isinstance(k,str):
                            k = str(k)
                        if isinstance(v,list):
                            v = " -- ".join([str(e) for e in v])
                        elif not isinstance(v,str):
                            v = str(v)
                            
                        d.update({k: v})
                return d
        for ele in self._builder.run_procedure(module,name,params):
            print(ele)
            final_elements.append(iterdict(ele))
        return final_elements