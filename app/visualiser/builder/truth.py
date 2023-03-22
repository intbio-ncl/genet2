from app.visualiser.builder.abstract import AbstractBuilder
from app.visualiser.builder.builders.design.hierarchy import HierarchyViewBuilder
from app.visualiser.builder.builders.design.interaction import InteractionViewBuilder
from app.visualiser.builder.builders.design.interaction_explicit import InteractionExplicitViewBuilder
from app.visualiser.builder.builders.design.interaction_genetic import InteractionGeneticViewBuilder
from app.visualiser.builder.builders.design.interaction_protein import InteractionProteinViewBuilder
from app.visualiser.builder.builders.design.interaction_verbose import InteractionVerboseViewBuilder
from app.visualiser.builder.builders.design.interaction_io import InteractionIoViewBuilder
from app.visualiser.builder.builders.design.pruned import PrunedViewBuilder
from app.visualiser.builder.builders.full import FullViewBuilder

class TruthBuilder(AbstractBuilder):
    def __init__(self,graph):
        super().__init__(graph)
        self._dg = graph.truth
        self._view_builder = FullViewBuilder(self._dg)

    def v_nodes(self):
        return self.view.nodes(reserved=True)

    def v_edges(self,n=None):
        return self.view.edges(n,reserved=True)

    def in_edges(self, n=None):
        return self.view.in_edges(n,reserved=True)

    def out_edges(self, n=None):
        return self.view.out_edges(n,reserved=True)
    
    def set_full_view(self):
        self._view_builder = FullViewBuilder(self._dg)

    def set_pruned_view(self):
        self._view_builder = PrunedViewBuilder(self._dg)
         
    def set_hierarchy_view(self):
        self._view_builder = HierarchyViewBuilder(self._dg)

    def set_interaction_explicit_view(self):
        self._view_builder = InteractionExplicitViewBuilder(self._dg)

    def set_interaction_verbose_view(self):
        self._view_builder = InteractionVerboseViewBuilder(self._dg)

    def set_interaction_view(self):
        self._view_builder = InteractionViewBuilder(self._dg)

    def set_interaction_genetic_view(self):
        self._view_builder = InteractionGeneticViewBuilder(self._dg)

    def set_interaction_protein_view(self):
        self._view_builder = InteractionProteinViewBuilder(self._dg)

    def set_interaction_io_view(self):
        self._view_builder = InteractionIoViewBuilder(self._dg)
        
    def get_loaded_design_names(self):
        return self._builder.get_loaded_design_names()

    def get_root_entities(self):
        return self._dg.get_root_entities()