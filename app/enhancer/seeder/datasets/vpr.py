import os
import json
from rdflib import URIRef
from app.enhancer.seeder.datasets.abstract_dataset import AbstractDatabase
from app.converter.utility.graph import SBOLGraph
from app.converter.utility.identifiers import identifiers as ids

vpr_records = os.path.join(os.path.dirname(os.path.realpath(__file__)),"vpr_records.json")
vpr_graph =  os.path.join(os.path.dirname(os.path.realpath(__file__)),"vpr_graph.xml")
cd_pred = ids.objects.component_definition
md_pred = ids.objects.module_definition
class VPR(AbstractDatabase):
    def __init__(self,graph,miner,aligner):
        super().__init__(graph,miner,aligner)

    def build(self):
        if os.path.isfile(vpr_graph):
            return vpr_graph
        if not os.path.isfile(vpr_records):
            self._miner.get_vpr_data(vpr_records)
        graph = SBOLGraph()
        with open(vpr_records) as f:
            vpr_recs = json.load(f)
            seqs = {}
            for identity in vpr_recs[str(cd_pred)]:
                identity = URIRef(identity)
                record = SBOLGraph(self._miner.get_external(identity))
                if record is None:
                    continue
                ret,seqs = self._handle_component_definition(record,identity,seqs)
                if ret is not None:
                    graph += ret
            for identity in vpr_recs[str(md_pred)]:
                identity = URIRef(identity)
                record = SBOLGraph(self._miner.get_external(identity))
                graph += record

        seqs = graph.get_sequences()
        seen = set()
        dupes = []

        for x in seqs:
            if x in seen:
                dupes.append(x)
            else:
                seen.add(x)

        for d in dupes:
            sns = graph.get_sequence_names(sequence=d)
            assert(len(sns) > 1)
            orig_seq = sns.pop()
            orig = graph.get_component_definitions(seq_name=orig_seq)
            assert(len(orig) == 1)
            for sn in sns:
                cd = graph.get_component_definitions(seq_name=sn)
                assert(len(cd) == 1)
                graph = self._replace_cd(graph,orig[0],cd[0])
        graph.save(vpr_graph)
        return vpr_graph

    def integrate(self,threshold,existing_seqs=None,existing_ints=None,existing_non_dna=None):
        if not os.path.isfile(vpr_graph):
            self.build()
        ig_graph = SBOLGraph(vpr_graph)
        print(f'Considering Vpr: CDS: {len(ig_graph.get_component_definitions())}, Interactions: {len(ig_graph.get_interactions())}')
        return super().integrate(ig_graph,threshold,existing_seqs,existing_ints,existing_non_dna)