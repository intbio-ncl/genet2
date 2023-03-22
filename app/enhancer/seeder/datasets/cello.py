import os
from rdflib import URIRef
from app.enhancer.seeder.datasets.abstract_dataset import AbstractDatabase
from app.converter.utility.graph import SBOLGraph
from  app.converter.utility.identifiers import identifiers as ids

cello_vpr_fn = os.path.join(os.path.dirname(os.path.realpath(__file__)),"cello_vpr.xml")

class Cello(AbstractDatabase):
    def __init__(self,graph,miner,aligner):
        super().__init__(graph,miner,aligner)

    def build(self):
        if not os.path.isfile(cello_vpr_fn):
            graph = self._integrate_ecoli(self._build_cello(), self._build_ecoli())
            graph.save(cello_vpr_fn)
        return cello_vpr_fn
    
    def integrate(self,threshold,existing_seqs=None,existing_ints=None,existing_non_dna=None):
        if not os.path.isfile(cello_vpr_fn):
            self.build()
        ig_graph = SBOLGraph(cello_vpr_fn)
        print(f'Considering Cello: CDS: {len(ig_graph.get_component_definitions())}, Interactions: {len(ig_graph.get_interactions())}')
        return super().integrate(ig_graph,threshold,existing_seqs,existing_ints,existing_non_dna)
    
    def _build_cello(self):
        graph = SBOLGraph(self._miner.get_external("Cello_Parts_collection",timeout=80))
        seqs = {}
        for cd in graph.get_component_definitions():
            cd = URIRef(cd)
            types = graph.get_types(cd)
            if ids.roles.DNARegion not in types:
                continue
            ret,seqs = self._handle_component_definition(graph,cd,seqs)
            if ret is None:
                graph.remove_component_definition(cd)
                continue
            graph = ret
        return graph
        
    def _build_ecoli(self):
        graph = SBOLGraph(self._miner.get_external("GokselEco1C1G1T2_collection",timeout=80))
        cds = graph.get_component_definitions()
        seqs = {}
        for cd in cds:
            types = graph.get_types(cd)
            if ids.roles.DNARegion in types:
                cd_seq = graph.get_sequences(cd)
                cmpts = graph.get_components(cd)
                for cmp in cmpts:
                    cdef = graph.get_definition(cmp)
                    if graph.get_sequences(cdef) == cd_seq:
                        graph.remove_component(cmp)
                        self._replace_cd(graph,cdef,cd)
                        break
                else:
                    if self._has_components(cd,graph):
                        graph.remove_component_definition(cd)
                        continue
                    assert(len(cd_seq) == 1)
                    cd_seq = cd_seq[0]
                    if cd_seq in seqs:
                        graph = self._replace_cd(graph,seqs[cd_seq],cd)
                    else:
                        seqs[cd_seq] = cd
            
        graph = self._prune_sbol_predicates(graph)
        graph = self._prune_sbol_objects(graph)
        return graph

    def _integrate_ecoli(self,g_cello,g_ecoli):
        g_cello_dna = {}
        g_cello_ng = {}
        # Reduces number of graph queries.
        for cd in g_cello.get_component_definitions():
            seq = g_cello.get_sequences(cd)
            types = g_cello.get_types(cd)
            if ids.roles.DNARegion not in types:
                g_cello_ng[self._get_name(cd).lower()] = cd
                continue
            roles = g_cello.get_roles(cd)
            assert(len(seq) == 1)
            seq = seq[0].lower()
            assert(seq not in g_cello_dna)
            g_cello_dna[seq] = [cd,roles]

        for cd in g_ecoli.get_component_definitions():
            cd_type = g_ecoli.get_types(cd)
            if ids.roles.DNARegion in cd_type:
                e_seq = g_ecoli.get_sequences(cd)
                assert(len(e_seq) == 1)
                l_e_seq = e_seq[0].lower()
                if l_e_seq in g_cello_dna:
                    c_cds = g_cello_dna[l_e_seq][0]
                    g_ecoli = self._replace_cd(g_ecoli,c_cds,cd)
            else:
                name = self._get_name(cd).lower()
                if name in g_cello_ng:
                    g_ecoli = self._replace_cd(g_ecoli,g_cello_ng[name],cd)
        
        
        graph = g_cello + g_ecoli
        # Remove any duplicate interactions
        i_dict = {}
        for i in graph.get_interactions():
            i_type = graph.get_types(i)[0]
            if i_type not in i_dict:
                i_dict[i_type] = []
            parts = []
            for p in graph.get_participants(interaction=i):
                p_role = str(graph.get_roles(p)[0])
                fc = graph.get_participant(p)
                fc_def = graph.get_definition(fc)
                parts.append(f'{p_role} - {fc_def}')
            
            for e_parts in i_dict[i_type]:
                if len(e_parts) != len(parts):
                    continue
                if len(list(set(e_parts) & set(parts))) == len(e_parts):
                    graph.remove_interaction(i)
                    break
            else:
                i_dict[i_type].append(parts)
        # Remove redundant moduleDefs
        for md in graph.get_module_definition():
            if len(graph.get_interactions(md=md)) + len(graph.get_modules(md)) == 0:
                graph.remove_module_definition(md)
        return graph



    
