import os
import json
from rdflib import URIRef
from app.enhancer.seeder.datasets.abstract_dataset import AbstractDatabase
from app.converter.utility.graph import SBOLGraph

igem_cds = os.path.join(os.path.dirname(os.path.realpath(__file__)),"igem_cds.json")
sbh_igem =  os.path.join(os.path.dirname(os.path.realpath(__file__)),"sbh_igem.xml")
igem_fasta = "http://parts.igem.org/fasta/parts/All_Parts"
sbh_igem_prefix = "https://synbiohub.org/public/igem/"

class IGEM(AbstractDatabase):
    def __init__(self,graph,miner,aligner):
        super().__init__(graph,miner,aligner)


    def build(self):
        if os.path.isfile(sbh_igem):
            return sbh_igem
        if not os.path.isfile(igem_cds):
            self._miner.download_igem_parts(igem_cds)
        graph = SBOLGraph()
        seqs = {}
        with open(igem_cds) as f:
            igem_recs = json.load(f)
            for identity in igem_recs:
                identity = URIRef(identity)
                record = SBOLGraph(self._miner.get_external(identity))
                if record is None:
                    continue
                ret,seqs = self._handle_component_definition(record,identity,seqs)
                if ret is not None:
                    graph += ret
        graph.save(sbh_igem)
        return sbh_igem


    def integrate(self,threshold,existing_seqs=None,existing_ints=None,existing_non_dna=None):
        if not os.path.isfile(sbh_igem):
            self.build()
        ig_graph = SBOLGraph(sbh_igem)
        print(f'Considering IGEM: CDS: {len(ig_graph.get_component_definitions())}, Interactions: {len(ig_graph.get_interactions())}')
        return super().integrate(ig_graph,threshold,existing_seqs,existing_ints,existing_non_dna)








