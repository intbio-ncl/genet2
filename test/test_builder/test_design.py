import unittest
import os
import sys
from rdflib import URIRef

sys.path.insert(0, os.path.join(".."))
sys.path.insert(0, os.path.join("..",".."))
sys.path.insert(0, os.path.join("..","..",".."))

from app.visualiser.builder.design import DesignBuilder
from app.graph.world_graph import WorldGraph
from  app.graph.utility.model.model import model
from app.converter.sbol_convert import convert

curr_dir = os.path.dirname(os.path.realpath(__file__))
test_fn = os.path.join(curr_dir,"..","files","nor_full.xml")


class TestViews(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.gn = "test_builder_views"
        self.wg = WorldGraph()
        convert(test_fn,self.wg.driver,self.gn)
        self.dg = self.wg.get_design(self.gn)
        self.all_nodes = self.dg.nodes()
        self.all_edges = self.dg.edges()
        self.builder = DesignBuilder(self.wg)
        self.builder.set_design(self.dg)

    @classmethod
    def tearDownClass(self):
        self.wg.remove_design(self.gn)
    
    def tearDown(self):
        self.builder.set_design(self.dg)

    def test_full(self):
        self.builder.set_full_view()
        self.builder.build()
        graph = self.builder.view
        view_edges = graph.edges()
        self.assertCountEqual(self.all_edges,view_edges)
            
    def test_pruned(self):
        self.builder.set_pruned_view()
        self.builder.build()
        graph = self.builder.view
        self.assertTrue(len(graph) > 0)
        for edge in graph.edges():
            self.assertTrue(edge.get_type()) in model.identifiers.predicates

    def test_heirarchy(self):
        self.builder.set_hierarchy_view()
        self.builder.build()
        graph = self.builder.view
        for n in graph.nodes():
            actual_children = [c for c in graph.edges(n)]
            expected_children = self.dg.get_children(n)
            self.assertEqual(expected_children, actual_children)

    def test_interaction_explicit(self):
        self.builder.set_interaction_explicit_view()
        self.builder.build()
        graph = self.builder.view
        physical_entity_obj = model.identifiers.objects.physical_entity
        reaction_entity_obj = model.identifiers.objects.reaction
        reaction_class_code = model.get_class_code(reaction_entity_obj)
        pe_class_code = model.get_class_code(physical_entity_obj)
        self.assertTrue(len(graph) > 0)
        for edge in graph.edges():
            n = edge.n
            v = edge.v
            n_type = URIRef(n.get_type())
            v_type = URIRef(v.get_type())
            if model.is_derived(n_type,pe_class_code):
                self.assertTrue(model.is_derived(v_type,reaction_class_code))
            elif model.is_derived(n_type,reaction_class_code):
                self.assertTrue(model.is_derived(v_type,reaction_class_code) or 
                                model.is_derived(v_type,pe_class_code))
            else:
                self.fail("n is not a physc, inter or react.")

    def test_interaction_verbose(self):
        self.builder.set_interaction_verbose_view()
        self.builder.build()
        graph = self.builder.view
        interaction_obj = model.identifiers.objects.interaction
        physical_entity_obj = model.identifiers.objects.physical_entity
        interaction_class_code = model.get_class_code(interaction_obj)
        pe_class_code = model.get_class_code(physical_entity_obj)
        interactions_classes = [str(d[1]["key"]) for d in model.get_derived(interaction_class_code)]
        self.assertTrue(len(graph) > 0)
        for edge in graph.edges():
            n = edge.n
            v = edge.v
            n_type = n.get_type()
            v_type = v.get_type()
            if n_type in interactions_classes:
                self.assertTrue(model.is_derived(URIRef(v_type),pe_class_code))
            elif v_type in interactions_classes:
                self.assertTrue(model.is_derived(URIRef(v_type),interaction_class_code))
            else:
                self.fail("Neither node is an interaction.")
    
    def test_interaction(self):
        self.builder.set_interaction_view()
        self.builder.build()
        graph = self.builder.view
        interaction_obj = model.identifiers.objects.interaction
        physical_entity_obj = model.identifiers.objects.physical_entity
        interaction_class_code = model.get_class_code(interaction_obj)
        pe_class_code = model.get_class_code(physical_entity_obj)
        interactions_classes = [str(d[1]["key"]) for d in model.get_derived(interaction_class_code)]
        pe_classes = [str(d[1]["key"]) for d in model.get_derived(pe_class_code)]
        self.assertTrue(len(graph) > 0)
        for edge in graph.edges():
            n = edge.n
            v = edge.v
            n_type = n.get_type()
            v_type = v.get_type()
            self.assertTrue(edge.get_type() in interactions_classes)
            self.assertTrue(n_type in pe_classes)
            self.assertTrue(v_type in pe_classes)
            
    def test_interaction_genetic(self):
        self.builder.set_interaction_genetic_view()
        self.builder.build()
        graph = self.builder.view
        interaction_obj = model.identifiers.objects.interaction
        dna_obj = model.identifiers.objects.dna
        interaction_class_code = model.get_class_code(interaction_obj)
        dna_class_code = model.get_class_code(dna_obj)
        interactions_classes = [str(d[1]["key"]) for d in model.get_derived(interaction_class_code)]
        dna_classes = [str(d[1]["key"]) for d in model.get_derived(dna_class_code)] + [dna_obj]
        self.assertTrue(len(graph) > 0)
        for edge in graph.edges():
            n = edge.n
            v = edge.v
            n_type = n.get_type()
            v_type = v.get_type()
            self.assertTrue(edge.get_type() in interactions_classes)
            self.assertTrue(n_type in dna_classes)
            self.assertTrue(v_type in dna_classes)

    def test_interaction_protein(self):
        self.builder.set_interaction_protein_view()
        self.builder.build()
        graph = self.builder.view
        interaction_obj = model.identifiers.objects.interaction
        prot_obj = model.identifiers.objects.protein
        interaction_class_code = model.get_class_code(interaction_obj)
        prot_class_code = model.get_class_code(prot_obj)
        interactions_classes = [str(d[1]["key"]) for d in model.get_derived(interaction_class_code)]
        protein_classes = [str(prot_obj)] + [str(d[1]["key"]) for d in model.get_derived(prot_class_code)]
        self.assertTrue(len(graph) > 0)
        for edge in graph.edges():
            n = edge.n
            v = edge.v
            n_type = n.get_type()
            v_type = v.get_type()
            self.assertTrue(edge.get_type() in interactions_classes)
            self.assertTrue(n_type in protein_classes)
            self.assertTrue(v_type in protein_classes)

    def test_interaction_io(self):
        self.builder.set_interaction_io_view()
        self.builder.build()
        graph = self.builder.view
        self.assertTrue(len(graph) > 0)        

    def test_views_multiple_graphs_any(self):
        gn1 = "test_wg_get_all1"
        gn2 = "test_wg_get_all2"
        gn3 = "test_wg_get_all3"

        fn1 = os.path.join(curr_dir,"..","..","test","files","0xC7.xml")
        fn2 = os.path.join(curr_dir,"..","..","test","files","0x87.xml")
        fn3 = os.path.join(curr_dir,"..","..","test","files","0x3B.xml")

        convert(fn1,self.wg.driver,gn1)
        convert(fn2,self.wg.driver,gn2)
        convert(fn3,self.wg.driver,gn3)

        dg1 = self.wg.get_design([gn1],predicate="ANY")
        self.builder.set_design(dg1)
        self.builder.set_interaction_view()
        self.builder.build()
        graph1 = self.builder.view
        edges1 = list(graph1.edges())

        dg2 = self.wg.get_design([gn2],predicate="ANY")
        self.builder.set_design(dg2)
        self.builder.set_interaction_view()
        self.builder.build()
        graph2 = self.builder.view
        edges2 = list(graph2.edges())

        dg3 = self.wg.get_design([gn3],predicate="ANY")
        self.builder.set_design(dg3)
        self.builder.set_interaction_view()
        self.builder.build()
        graph3 = self.builder.view
        edges3 = list(graph3.edges())

        adg = self.wg.get_design([gn1,gn2,gn3],predicate="ANY")
        self.builder.set_design(adg)
        self.builder.set_interaction_view()
        self.builder.build()
        graph = self.builder.view
        for e in graph.edges():
            self.assertTrue(e in edges1 or e in edges2 or e in edges3)

        self.wg.remove_design(gn1)
        self.wg.remove_design(gn2)
        self.wg.remove_design(gn3)



def diff(list1,list2):
    diff = []
    for n,v,e in list1:
        for n1,v1,e1 in list2:
            if n == n1 and v == v1 and e == e1:
                break
        else:
            diff.append((n,v,e,k))
    return diff


if __name__ == '__main__':
    unittest.main()
