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
nv_p = model.identifiers.objects.protein
nv_pp = model.identifiers.objects.genetic_production
nv_template = model.identifiers.predicates.template
nv_product = model.identifiers.predicates.product

class ProteinProductionEnhancement(AbstractEnhancement):
    def __init__(self, world_graph, miner):
        super().__init__(world_graph, miner)

    def enhance(self, graph):
        graph = self._wg.get_design(graph)
        for cds in graph.get_cds():
            for i in graph.get_interactions(cds):
                if i.n.get_type() == str(nv_pp):
                    break
            else:
                n = self._add_related_node(graph,cds,nv_p)
                v = self._add_related_node(graph,cds,nv_pp)
                e = [(cds,nv_template),
                     (n,nv_product)]
                self._add_interaction(graph,v,e,100)
        