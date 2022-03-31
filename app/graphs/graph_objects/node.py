from app.graphs.graph_objects.graph_object import GraphObject


class Node(GraphObject):
    def __init__(self,labels,id=None, **kwargs):
        super().__init__(labels, id=id,**kwargs)

    def duplicate(self):
        return self.__class__(self.labels.copy(),**self.properties)
        
    def __eq__(self, obj):
        if not isinstance(obj, self.__class__):
            return False
        if obj.labels == self.labels:
            return True
        return False
        
    def __hash__(self):
        return hash(str(self.labels))
