from app.enhancer.enhancements.abstract_enhancements import AbstractEnhancement
from app.graph.utility.model.model import model


class DesignInference(AbstractEnhancement):
    def __init__(self, world_graph, miner):
        super().__init__(world_graph, miner)
    

class TruthInference(AbstractEnhancement):
    def __init__(self, world_graph, miner):
        super().__init__(world_graph, miner)
