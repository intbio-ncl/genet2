from graph.abstract import AbstractGraph

class DesignGraph(AbstractGraph):
    def __init__(self,graph=None):
        super().__init__(graph)
        if graph:
            self._generate_labels()
        



