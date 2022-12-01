from app.enhancer.enhancements.abstract_enhancements import AbstractEnhancement
from app.enhancer.enhancements.interaction import InteractionEnhancement
class Enhancements(AbstractEnhancement):
    def __init__(self,world_graph,miner):
        super().__init__(world_graph,miner,[InteractionEnhancement])
        