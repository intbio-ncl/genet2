from app.graphs.graph_objects.graph_object import GraphObject

class Edge(GraphObject):
    def __init__(self,n,v,labels,id=None,**kwargs):
        super().__init__(labels,id=id,**kwargs)
        self.n = n
        self.v = v

    def duplicate(self):
        return self.__class__(self.n.duplicate(),self.v.duplicate(),
                              self.labels.copy(),**self.properties)
                              
    def __str__(self):
        return f'{self.n} - {super().__str__()} - {self.v}'

    def __eq__(self, obj):
        if not isinstance(obj, self.__class__):
            return False
        if obj.n == self.n and obj.labels == self.labels and obj.v == self.v:
            return True
        return False

    def __hash__(self):
        return hash(str(self.labels+self.n.labels+self.v.labels))