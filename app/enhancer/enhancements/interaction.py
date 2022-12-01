from app.enhancer.enhancements.abstract_enhancements import AbstractEnhancement
from app.graph.utility.model.model import model
ids = model.identifiers

part_int_map = {
    str(ids.objects.promoter): [str(ids.objects.activation)],
    str(ids.objects.cds): [str(ids.objects.genetic_production)],
    str(ids.objects.protein): [str(ids.objects.repression)],
    str(ids.objects.complex): [str(ids.objects.activation)],
    str(ids.objects.smallmolecule): [str(ids.objects.binds)]
}

nv_i = model.identifiers.objects.input
nv_o = model.identifiers.objects.output

class InteractionEnhancement(AbstractEnhancement):
    def __init__(self, world_graph, miner):
        super().__init__(world_graph, miner)

    def enhance(self, graph):
        print(graph)
        pass