import sys
import os
import unittest
import copy

sys.path.insert(0, os.path.join(".."))
sys.path.insert(0, os.path.join("..",".."))
sys.path.insert(0, os.path.join("..","..",".."))
sys.path.insert(0, os.path.join("..","..","..",".."))
from app.converter.utility.identifiers import identifiers
from app.graph.world_graph import WorldGraph
from app.enhancer.enhancer import Enhancer
from app.enhancer.seeder.seeder import Seeder
from app.converter.utility.graph import SBOLGraph
from  app.converter.utility.identifiers import identifiers as ids
curr_dir = os.path.dirname(os.path.realpath(__file__))
fn = os.path.join("test","files","nor_full.xml")

class TestEnhancer(unittest.TestCase):
    
    @classmethod
    def setUpClass(self):
        self.gn = "test_enhancer"
        self.wg = WorldGraph()
        self.enhancer = Enhancer(self.wg)
        self.miner = self.enhancer._miner

    @classmethod
    def tearDownClass(self):
        self.wg.remove_design(self.gn)

    # --- Evaluate ---
    def test_evaluate_design(self):
        pass
    
    def test_get_evaluators(self):
        pass

    # --- Truth ---

    def test_apply_truth_graph(self):
        pass

    # --- Design --- 
    def test_enhance_truth_graph(self):
        pass

    def test_apply_truth_graph(self):
        pass

class TestSeeder(unittest.TestCase):
    
    @classmethod
    def setUpClass(self):
        self.gn = "test_enhancer"
        self.wg = WorldGraph()
        self.enhancer = Enhancer(self.wg)
        self.miner = self.enhancer._miner
        self.seeder = Seeder(self.enhancer._graph.truth,self.enhancer._miner)


    @classmethod
    def tearDownClass(self):
        self.wg.remove_design(self.gn)

    def test_enable_disable(self):
        self.seeder.enable_igem()
        self.seeder.enable_vpr()
        self.seeder.enable_cello()
        for i,enabled in self.seeder._datasets.items():
            self.assertTrue(enabled)

        self.seeder.disable_igem()
        self.seeder.disable_vpr()
        self.seeder.disable_cello()
        for i,enabled in self.seeder._datasets.items():
            self.assertFalse(enabled)


    def test_cello_build_subgraph(self):
        ds = [s for s in self.seeder._datasets if s.__class__.__name__ == "Cello"][0]
        graph = ds._build_cello()
        self.assertEqual(len(graph.get_maps_to()),0)
        cds = graph.get_component_definitions()
        mds = graph.get_module_definition()
        for cd in cds:
            comps = graph.get_components(cd)
            self.assertEqual(len(comps),0)
            for hi in graph.get_heirachical_instances(cd):
                self.assertIn(graph.get_parent(hi),cds)
            for fi in graph.get_functional_instances(cd):
                self.assertIn(graph.get_parent(fi),mds)
                for part in graph.get_participants(fc=fi):
                    ints = graph.get_interactions(participation=part)
                    self.assertGreater(len(ints),0)        
                    self.assertIn(graph.get_parent(part),ints)


    def test_build_ecoli(self):
        ds = [s for s in self.seeder._datasets if s.__class__.__name__ == "Cello"][0]
        graph = ds._build_ecoli()
        print(len(graph),len(graph.get_component_definitions()),len(graph.get_interactions()))
        cds = graph.get_component_definitions()
        mds = graph.get_module_definition()
        for cd in cds:
            comps = graph.get_components(cd)
            self.assertEqual(len(comps),0)
            for hi in graph.get_heirachical_instances(cd):
                self.assertIn(graph.get_parent(hi),cds)
            for fi in graph.get_functional_instances(cd):
                self.assertIn(graph.get_parent(fi),mds)
                for part in graph.get_participants(fc=fi):
                    ints = graph.get_interactions(participation=part)
                    self.assertGreater(len(ints),0)        
                    self.assertIn(graph.get_parent(part),ints)


    def test_integrate_ecoli(self):
        ds = [s for s in self.seeder._datasets if s.__class__.__name__ == "Cello"][0]
        c_g = ds._build_cello()
        e_g = ds._build_ecoli()
        pre_c_is = c_g.get_interactions()
        pre_e_is = e_g.get_interactions()
        f_graph = ds._integrate_ecoli(c_g,e_g)
        cds = f_graph.get_component_definitions()
        mds = f_graph.get_module_definition()
        for cd in cds:
            for c in f_graph.get_components(cd):
                c_def = f_graph.get_definition(c)
                self.assertIn(c_def,cds)
                self.assertNotEqual(c_def,cd)
            for hi in f_graph.get_heirachical_instances(cd):
                self.assertIn(f_graph.get_parent(hi),cds)
            for fi in f_graph.get_functional_instances(cd):
                self.assertIn(f_graph.get_parent(fi),mds)
                for part in f_graph.get_participants(fc=fi):
                    ints = f_graph.get_interactions(participation=part)
                    self.assertGreater(len(ints),0)        
                    self.assertIn(f_graph.get_parent(part),ints)

        post_is = f_graph.get_interactions()
        #self.assertEqual(len(post_is),len(pre_c_is+pre_e_is))
        for interaction in post_is:
            parts = f_graph.get_participants(interaction=interaction)
            types = f_graph.get_types(interaction)
            if identifiers.roles.degradation in types:
                self.assertEqual(len(parts),1)
                fc = f_graph.get_participant(parts[0])
                definition = f_graph.get_definition(fc)
                self.assertIn(definition,cds)
            else:
                self.assertGreater(len(parts),1)
                for p in parts:
                    fc = f_graph.get_participant(p)
                    definition = f_graph.get_definition(fc)
                    self.assertIn(definition,cds)
        # Check for duplicates.
        seen = set()
        dupes = []
        for x in f_graph.get_sequences():
            if x in seen:
                dupes.append(x)
            else:
                seen.add(x)
        self.assertEqual(len(dupes),0)


    def test_cello_build(self):
        ds = [s for s in self.seeder._datasets if s.__class__.__name__ == "Cello"][0]
        fn = ds.build()
        g = SBOLGraph(fn)

        seqs = g.get_sequences()
        for seq in seqs:
            seq_names = g.get_sequence_names(sequence=seq)
            self.assertEqual(len(seq_names),1)
            cds = g.get_component_definitions(seq_name = seq_names[0])
            self.assertEqual(len(cds),1)
        seqs = [s.lower() for s in seqs]
        self.assertEqual(len(seqs),len(list(set(seqs))))
        
        ints_cds = []
        for i in g.get_interactions():
            parts = g.get_participants(interaction=i)
            cds = []
            for p in parts:
                cds.append(g.get_definition(g.get_participant(p)))
            ints_cds.append(cds)        
        
        new_k = []
        for elem in ints_cds:
            self.assertFalse(elem in new_k)
            new_k.append(elem)
        self.assertEqual(len(ints_cds),len(new_k))


    def test_vpr_build(self):
        ds = [s for s in self.seeder._datasets if s.__class__.__name__ == "VPR"][0]
        fn = ds.build()

        g = SBOLGraph(fn)
        seqs = g.get_sequences()
        for seq in seqs:
            seq_names = g.get_sequence_names(sequence=seq)
            for sn in seq_names:
                rdf_type = [p[2] for p in g.search((sn,identifiers.predicates.rdf_type,None))]
                self.assertEqual(rdf_type,[identifiers.objects.sequence],sn)
            self.assertEqual(len(seq_names),1,seq_names)
            cds = g.get_component_definitions(seq_name = seq_names[0])
            self.assertEqual(len(cds),1)
        seqs = [s.lower() for s in seqs]
        self.assertEqual(len(seqs),len(list(set(seqs))))

        cds = g.get_component_definitions()
        for i in g.get_interactions():
            for p in g.get_participants(interaction=i):
                fc= g.get_participant(p)
                defin = g.get_definition(fc)
                self.assertTrue(defin in cds)


    def test_igem_build(self):
        ds = [s for s in self.seeder._datasets if s.__class__.__name__ == "IGEM"][0]
        fn = ds.build()
        g = SBOLGraph(fn)

        seqs = g.get_sequences()
        for seq in seqs:
            seq_names = g.get_sequence_names(sequence=seq)
            self.assertEqual(len(seq_names),1)
            cds = g.get_component_definitions(seq_name = seq_names[0])
            self.assertEqual(len(cds),1)
        seqs = [s.lower() for s in seqs]
        self.assertEqual(len(seqs),len(list(set(seqs))))


    def test_igem_integrate(self):
        ds = [s for s in self.seeder._datasets if s.__class__.__name__ == "IGEM"][0]
        orig_graph = SBOLGraph(ds.build())
        es,ei,end = ds.integrate(0.8,{},{})
        tg = self.wg.truth
        pes = tg.get_dna()
        pes_names = [p.get_key() for p in pes]
        pes_sns = [p.hasSequence for p in pes]
        for cd in orig_graph.get_component_definitions():
            cd_type = orig_graph.get_types(cd)
            if identifiers.roles.DNARegion in cd_type:
                sequence = orig_graph.get_sequence_names(cd)
                if cd in es.values():
                    self.assertIn(str(cd),pes_names)
                else:
                    self.assertNotIn(str(cd),pes_names)
                for s in sequence:
                    s = str(s)
                    self.assertIn(s,pes_sns)
            else:
                self.assertIn(cd,end)
                self.assertEqual(cd_type,end[cd])

        tg_is = tg.get_interactions()
        tg_names = list(set([p.n.get_key() for p in tg_is]))
        for i in orig_graph.get_interactions():
            i_type = orig_graph.get_types(i)
            i_data = []
            inputs,outputs = tg.get_interaction_io(i)
            tg_elements = [i.v.get_key() for i in inputs] + [o.v.get_key() for o in outputs]
            parts = orig_graph.get_participants(interaction=i)
            for p in parts:
                p_role = orig_graph.get_roles(p)
                fc = orig_graph.get_participant(p)
                fc_def = orig_graph.get_definition(fc)
                for r in p_role:
                    i_data.append(f'{r}{fc_def}')
                self.assertIn(str(fc_def),tg_elements)
            self.assertIn(str(i),tg_names)
            for i_t in i_type:
                self.assertIn(i_t,ei.keys())
                for part in ei[i_t]:
                    if part == i_data:
                        break
                else:
                    self.fail()


    def test_vpr_integrate(self):
        ds = [s for s in self.seeder._datasets if s.__class__.__name__ == "VPR"][0]
        orig_graph = SBOLGraph(ds.build())
        es,ei,end = ds.integrate(0.8,{},{})
        tg = self.wg.truth
        pes = tg.get_dna()
        pes_names = [p.get_key() for p in pes]
        pes_sns = [p.hasSequence for p in pes]

        for cd in orig_graph.get_component_definitions():
            cd_type = orig_graph.get_types(cd)
            if identifiers.roles.DNARegion in cd_type:
                sequence = orig_graph.get_sequence_names(cd)
                if cd in es.values():
                    self.assertIn(str(cd),pes_names)
                else:
                    self.assertNotIn(str(cd),pes_names)
                for s in sequence:
                    s = str(s)
                    self.assertIn(s,pes_sns)
            else:
                self.assertIn(cd,end)
                self.assertEqual(cd_type,end[cd])

        tg_is = tg.get_interactions()
        tg_names = list(set([p.n.get_key() for p in tg_is]))
        for i in orig_graph.get_interactions():
            i_type = orig_graph.get_types(i)
            i_data = []
            inputs,outputs = tg.get_interaction_io(i)
            tg_elements = [i.v.get_key() for i in inputs] + [o.v.get_key() for o in outputs]
            parts = orig_graph.get_participants(interaction=i)
            for p in parts:
                p_role = orig_graph.get_roles(p)
                fc = orig_graph.get_participant(p)
                fc_def = orig_graph.get_definition(fc)
                for r in p_role:
                    i_data.append(f'{r}{fc_def}')
                self.assertIn(str(fc_def),tg_elements)
            self.assertIn(str(i),tg_names)
            for i_t in i_type:
                self.assertIn(i_t,ei.keys())
                for part in ei[i_t]:
                    if part == i_data:
                        break
                else:
                    self.fail()


    def test_cello_integrate(self):
        ds = [s for s in self.seeder._datasets if s.__class__.__name__ == "Cello"][0]
        orig_graph = SBOLGraph(ds.build())
        es,ei,end = ds.integrate(0.8,{},{})
        tg = self.wg.truth
        pes = tg.get_dna()
        pes_names = [p.get_key() for p in pes]
        pes_sns = [p.hasSequence for p in pes]
        for cd in orig_graph.get_component_definitions():
            cd_type = orig_graph.get_types(cd)
            if identifiers.roles.DNARegion in cd_type:
                sequence = orig_graph.get_sequence_names(cd)
                if cd in es.values():
                    self.assertIn(str(cd),pes_names)
                else:
                    self.assertNotIn(str(cd),pes_names)
                for s in sequence:
                    s = str(s)
                    self.assertIn(s,pes_sns)
            else:
                self.assertIn(cd,end)
                self.assertEqual(cd_type,end[cd])

        tg_is = tg.get_interactions()
        tg_names = list(set([p.n.get_key() for p in tg_is]))
        for i in orig_graph.get_interactions():
            i_type = orig_graph.get_types(i)
            i_data = []
            inputs,outputs = tg.get_interaction_io(i)
            tg_elements = [i.v.get_key() for i in inputs] + [o.v.get_key() for o in outputs]
            parts = orig_graph.get_participants(interaction=i)
            for p in parts:
                p_role = orig_graph.get_roles(p)
                fc = orig_graph.get_participant(p)
                fc_def = orig_graph.get_definition(fc)
                for r in p_role:
                    i_data.append(f'{r}{fc_def}')
                self.assertIn(str(fc_def),tg_elements)
            self.assertIn(str(i),tg_names)
            for i_t in i_type:
                self.assertIn(i_t,ei.keys())
                for part in ei[i_t]:
                    if part == i_data:
                        break
                else:
                    self.fail()


    def test_all_integrate(self):
        self.fail("Run this seperatley (And with backups), it will remove the truth graph.")
        self.seeder.enable_all()
        self.seeder.build()
        tg = self.wg.truth
        comps = {n.get_key(): n for n in tg.get_physicalentity()}
        synonyms = {e.v.get_key():e for e in tg.synonyms.get()}
        derivatives = {e.n.get_key():e for e in tg.derivatives.get()}
        orig_graph = SBOLGraph()
        for d in self.seeder._datasets.keys():
            gn = d.build()
            orig_graph += SBOLGraph(gn)
        cds = orig_graph.get_component_definitions()
        for cd in cds:
            str_cd = str(cd)
            if str_cd in comps:
                nv_node = comps[str_cd]
                cd_type = orig_graph.get_types(cd)
                if identifiers.roles.DNARegion in cd_type:
                    nv_seq = nv_node.hasSequence
                    sbol_seq = orig_graph.get_sequence_names(cd=cd)
                    self.assertEqual(len(sbol_seq),1)
                    self.assertEqual(nv_seq,str(sbol_seq[0]))
                    if str_cd in derivatives:
                        self.assertIn(derivatives[str_cd].v.get_key(),[str(s) for s in cds])
            else:
                self.assertIn(str_cd,synonyms)
        nv_ints = {}
        for e in tg.interactions.get():
            if e.n.get_key() in nv_ints:
                continue
            nv_ints[e.n.get_key()] = tg.get_interaction_elements(e.n)
        for i in orig_graph.get_interactions():
            parts = orig_graph.get_participants(interaction=i)
            fcs = [orig_graph.get_participant(p) for p in parts]
            defs = [str(orig_graph.get_definition(d)) for d in fcs]
            self.assertIn(str(i),nv_ints)
            nv_parts = [e.v.get_key() for e in nv_ints[str(i)]]
            for d in defs:
                if d not in nv_parts:
                    d = tg.synonyms.get(synonym=d)
                    self.assertTrue(len(d) > 0)
                    d = d[0].n.get_key()
                self.assertIn(d,nv_parts)
        





