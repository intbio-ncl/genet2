import dash_cytoscape as cyto
cyto.load_extra_layouts()
from app.visualiser.visual.abstract_design import AbstractDesignVisual
from app.visualiser.builder.editor import EditorBuilder

class EditorVisual(AbstractDesignVisual):
    def __init__(self,graph):
        super().__init__(EditorBuilder(graph))

    def get_io_nodes(self,predicate):
        return self._builder.get_io_nodes(predicate)
    
    def get_view_node_types(self):
        return self._builder.get_view_node_types()

    def get_view_nodes(self,identifier=None):
        return self._builder.get_view_nodes(identifier)

    def get_view_edge_types(self):
        return self._builder.get_view_edge_types()

    def add_edges(self,n,v,e):
        return self._builder.add_edges(n,v,e)
    
    def add_node(self,key,type,**kwargs):
        return self._builder.add_node(key,type,**kwargs)

    def get_standardised_nodes(self,key,type,sequence,description):
        return self._builder.get_standardised_nodes(key,type,sequence,description)


        
