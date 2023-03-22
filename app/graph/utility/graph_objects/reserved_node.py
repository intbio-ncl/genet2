from app.graph.utility.graph_objects.node import Node
from app.graph.utility.model.identifiers import KnowledgeGraphIdentifiers
nv_ids = KnowledgeGraphIdentifiers()
class ReservedNode(Node):
    def __init__(self,key,type=None,id=None, **kwargs): 
        if "graph_name" not in kwargs:
            raise ValueError("Reserved Nodes must have graph_names")
        super().__init__(key,type,id,**kwargs)
        self._confidence = nv_ids.external.confidence
        
    def __eq__(self, obj):
        if not super().__eq__(obj):
            return False
        if not hasattr(obj,"graph_name") and "graph_name" not in obj.get_properties():
            return False
        if len(list(set(self.graph_name) & set(obj.graph_name))) == 0:
            return False
        return True
        
    def __hash__(self):
        return hash(str(self.key))

    def __str__(self):
        return self.key

    def __getitem__(self, item):
        return self.properties[item]


