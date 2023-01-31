from app.enhancer.enhancements.abstract_enhancements import AbstractEnhancement
from app.graph.utility.model.model import model


class DesignTextExtraction(AbstractEnhancement):
    def __init__(self, world_graph, miner):
        super().__init__(world_graph, miner)
    
    def enhance(self, graph_name, mode="automated"):
        changes = {}
        for pe in self._wg.truth.get_physicalentity():
            for i,o in self._miner.interaction_search(pe.description):
                c = f'{pe} {i} {o}.'
                conf = 5
                change = [i,o]
                if mode == "automated":
                    self.apply(self._potential_change({},pe,change,conf,c,enabled=True),graph_name)
                else:
                    changes = self._potential_change(changes,pe,change,conf,c)
        return changes
        
class TruthTextExtraction(AbstractEnhancement):
    def __init__(self, world_graph, miner):
        super().__init__(world_graph, miner)

    def enhance(self, mode="automated"):
        return super().enhance(self._wg.truth.name, mode)
            
