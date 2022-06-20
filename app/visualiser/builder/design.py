from app.visualiser.viewgraph.viewgraph import ViewGraph 
from app.visualiser.builder.abstract import AbstractBuilder
from app.visualiser.builder.builders.design.view import ViewBuilder
from app.visualiser.builder.builders.design.mode import ModeBuilder

predicates = {"Intersection":"ALL",
              "Union":"ANY",
              "Difference":"SINGLE"}

class DesignBuilder(AbstractBuilder):
    def __init__(self,graph):
        super().__init__(graph)
        self._dg = self._graph.get_design(None)
        self.view = ViewGraph()
        self._view_h = ViewBuilder(self._dg)
        self._mode_h = ModeBuilder(self)
    
    def get_design_names(self):
        return self._graph.get_design_names()
    
    def get_load_predicates(self):
        return predicates.keys()

    def set_design_names(self,names,load_predicate):
        if load_predicate not in predicates:
            raise ValueError(f'{load_predicate} not valid load predicate, choices are: {str(predicates.keys())}')
        self.set_design(self._graph.get_design(names,predicates[load_predicate]))
    
    def set_design(self,design):
        self._dg = design
        self._view_h.set_graph(design)

    def get_children(self,node):
        return self._dg.get_children(node)
    
    def get_parents(self,node):
        return self._dg.get_parents(node)

    def get_entity_depth(self,subject):
        return self._dg.get_entity_depth(subject)

    def get_root_entities(self):
        return self._dg.get_root_entities()

    def set_pruned_view(self):
        self.view = self._view_h.pruned()
         
    def set_hierarchy_view(self):
        self.view = self._view_h.hierarchy()

    def set_interaction_explicit_view(self):
        self.view = self._view_h.interaction_explicit()

    def set_interaction_verbose_view(self):
        self.view = self._view_h.interaction_verbose()

    def set_interaction_view(self):
        self.view = self._view_h.interaction()

    def set_interaction_genetic_view(self):
        self.view = self._view_h.interaction_genetic()

    def set_interaction_protein_view(self):
        self.view = self._view_h.interaction_protein()

    def set_interaction_io_view(self):
        self.view = self._view_h.interaction_io()

    def set_module_view(self):
        self.view = self._view_h.module_view()
