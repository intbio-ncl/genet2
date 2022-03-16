from visual.handlers.abstract_label import AbstractNodeLabelHandler , AbstractEdgeLabelHandler

class LabelHandler:
    def __init__(self,builder):
        self.node = self.NodeLabelHandler(builder)
        self.edge = self.EdgeLabelHandler(builder)
    
    class NodeLabelHandler(AbstractNodeLabelHandler):
        def __init__(self,builder):
            super().__init__(builder)

    class EdgeLabelHandler(AbstractEdgeLabelHandler):
        def __init__(self,builder):
            super().__init__(builder)
        