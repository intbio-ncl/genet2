from app.graph.graph_objects.graph_object import GraphObject


class Node(GraphObject):
    def __init__(self, graph, labels, **kwargs):
        super().__init__(graph, labels, **kwargs)

    def __eq__(self, obj):
        if not isinstance(obj, self.__class__):
            return False
        if obj.labels == self.labels:
            return True
        return False
        
    def __hash__(self):
        return hash(str(self.labels))

    def degree(self):
        qry = self._graph.qry_builder.degree(
            self.labels, **self.get_properties())
        res = self._graph._run(qry)
        return res[0]["output"]

    def is_dense(self):
        qry = self._graph.qry_builder.is_dense(
            self.labels, **self.get_properties())
        res = self._graph._run(qry)
        return res[0]["output"]

    def is_connected(self, v):
        qry = self._graph.qry_builder.is_connected(
            self.labels, v.labels, self.get_properties(), v.get_properties())
        res = self._graph._run(qry)
        return res[0]["output"]
