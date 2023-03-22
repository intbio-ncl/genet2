from app.visualiser.visual.handlers.design.color import NodeColorHandler
from app.visualiser.visual.handlers.design.color import EdgeColorHandler
from app.visualiser.visual.handlers.color_producer import HSLVal

class TruthColorHandler():
    def __init__(self,builder):
        self.node = TruthNodeColorHandler(builder)
        self.edge = TruthEdgeColorHandler(builder)

class TruthNodeColorHandler(NodeColorHandler):
    def __init__(self,builder):
        super().__init__(builder)
    
class TruthEdgeColorHandler(EdgeColorHandler):
    def __init__(self,builder):
        super().__init__(builder)
    
    def confidence(self):
        colors = []
        for e in self._builder.v_edges():
            colors.append({str(e.confidence) : str(HSLVal(e.confidence,75,47))})
        return colors
