from app.graph.utility.graph_objects.edge import Edge
from app.graph.utility.model.identifiers import KnowledgeGraphIdentifiers
nv_ids = KnowledgeGraphIdentifiers()
class ReservedEdge(Edge):

    def __init__(self,n,v,type,id=None,**kwargs):
        if "graph_name" not in kwargs:
            raise ValueError("Reserved Edges must have graph_names")
        super().__init__(n,v,type,id,**kwargs)
        self._confidence = str(nv_ids.external.confidence)
        
    def __eq__(self, obj):
        if not super().__eq__(obj):
            return False
        if not hasattr(obj,"graph_name") and "graph_name" not in obj.get_properties():
            return False
        if len(list(set(self.graph_name) & set(obj.graph_name))) == 0:
            return False
        return True
        
    def __str__(self):
        return f'{self.n} - {self.type} - {self.v}'

    def __hash__(self):
        return hash(str(self.type+self.n.key+self.v.key))
        
    def __getitem__(self, item):
        return self.properties[item]


    @property
    def confidence(self):
        for k,v in self.properties.items():
            if k == self._confidence:
                return int(v)
        else:
            return None
    
    def set_confidence(self,val):
        self.properties[self._confidence] = int(val)

