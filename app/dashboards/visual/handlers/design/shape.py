from app.dashboards.visual.handlers.abstract_shape import AbstractNodeShapeHandler,AbstractEdgeShapeHandler

class ShapeHandler:
    def __init__(self,builder):
        self.node = self.NodeShapeHandler(builder)
        self.edge = self.EdgeShapeHandler()


    class NodeShapeHandler(AbstractNodeShapeHandler):
        def __init__(self,builder):
            super().__init__(builder)

            
    class EdgeShapeHandler(AbstractEdgeShapeHandler):
        def __init__(self):
            super().__init__()
