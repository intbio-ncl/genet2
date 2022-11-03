from app.graph.utility.graph_objects.edge import Edge
class ReservedEdge(Edge):

    def __init__(self,n,v,type,id=None,**kwargs):
        if "graph_name" not in kwargs:
            raise ValueError("Reserved Edges must have graph_names")
        super().__init__(n,v,type,id,**kwargs)
        
    def __eq__(self, obj):
        if not hasattr(obj,"graph_name") and "graph_name" not in obj.get_properties():
            return False
        if len(list(set(self.graph_name) & set(obj.graph_name))) == 0:
            return False

        return super().__eq__(obj)
        
    def __str__(self):
        return f'{self.n} - {self.type} - {self.v}'

    def __hash__(self):
        return hash(str(self.type+self.n.key+self.v.key))
        
    def __getitem__(self, item):
        return self.properties[item]


