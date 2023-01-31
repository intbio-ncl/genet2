from app.enhancer.enhancements.abstract_enhancements import AbstractEnhancement
from app.enhancer.enhancements.canonical.canonicaliser import TruthCanonicaliser
from app.enhancer.enhancements.interaction.protein_production import TruthProteinProduction

class TruthEnhancements(AbstractEnhancement):
    def __init__(self,world_graph,miner):
        super().__init__(world_graph,miner,[TruthCanonicaliser,
                                            TruthProteinProduction])