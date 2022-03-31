from cgi import test
import unittest
import os
import sys
from random import sample
from rdflib import RDF,BNode,URIRef

sys.path.insert(0, os.path.join(".."))
sys.path.insert(0, os.path.join("..",".."))
sys.path.insert(0, os.path.join("..","..",".."))

from app.dashboards.builder.design import DesignBuilder
from app.graphs.neo_graph.nv_graph import NVGraph

curr_dir = os.path.dirname(os.path.realpath(__file__))
test_fn = os.path.join(curr_dir,"..","files","design","sbol","output.xml")

class TestSearch(unittest.TestCase):
    def setUp(self):
        self._wrapper = NVGraph()
        self._backup = self._wrapper.get_all_edges()
        self._wrapper.purge()
        self._wrapper.add_graph(test_fn)
        self.builder = DesignBuilder(self._wrapper)
        self.builder.set_full_view()

    def tearDown(self):
        self._wrapper.purge()
        if len(self._backup) > 0:
            for edge in self._backup:
                n = self._wrapper.add_node(edge.n)
                v = self._wrapper.add_node(edge.v)
                self._wrapper.add_edge(n,v,edge)
            self._wrapper.submit()

    def test_nodes(self):
        all_nodes = self._wrapper.get_all_nodes()
        for n in self.builder.nodes():
            self.assertIn(n,all_nodes)

    def test_edges(self):
        all_edges = self._wrapper.get_all_edges()
        for edge in self.builder.edges():
            self.assertIn(edge,all_edges)

    def test_v_nodes(self):
        all_nodes = self._wrapper.get_all_nodes()
        for n in self.builder.v_nodes():
            self.assertIn(n,all_nodes)

    def test_v_edges(self):
        all_edges = self._wrapper.get_all_edges()
        for edge in self.builder.v_edges():
            self.assertIn(edge,all_edges)

    def test_out_edges(self):
        for n in self._wrapper.get_all_nodes():
            self.assertCountEqual(self._wrapper.edge_query(n), self.builder.out_edges(n))

    def test_get_rdf_type(self):
        rdf_types = self.builder.get_rdf_type()
        self.assertTrue(len(rdf_types) > 0)
        for edge in rdf_types:
            res = self.builder.get_rdf_type(edge.n)
            self.assertTrue(len(res),1)
            self.assertEqual(edge,res[0])
            
    def test_get_entities(self):
        entities = self.builder.get_entities()
        self.assertTrue(len(entities) > 0)
        for edge in entities:
            self.assertEqual(edge,self.builder.get_rdf_type(edge.n)[0])
        
    def test_get_interaction_io(self):
        for i in self.builder.get_interaction():
            inputs,outputs = self.builder.get_interaction_io(i.n)
            if len(inputs) > 0:
                self.assertCountEqual(inputs,self.builder._graph.edge_query(n=i.n,v=[e.v for e in inputs]))
            if len(outputs) > 0:
                self.assertCountEqual(outputs,self.builder._graph.edge_query(n=i.n,v=[e.v for e in outputs]))

    def test_get_entity_depth(self):
        for edge in self.builder.get_entities():
            depth = self.builder.get_entity_depth(edge.n)
            if self.builder.get_parents(edge.n) == []:
                self.assertEqual(depth,0)
            else:
                self.assertGreater(depth, 0)
    
    def test_get_entity_depth(self):
        for entity in self.builder.get_root_entities():
            self.assertEqual(self.builder.get_parents(entity),[])

class TestViews(unittest.TestCase):
    def setUp(self):
        self._wrapper = NVGraph()
        self._backup = self._wrapper.get_all_edges()
        self._wrapper.purge()
        self._wrapper.add_graph(test_fn)
        self.builder = DesignBuilder(self._wrapper)
        self.builder.set_full_view()

    def tearDown(self):
        self._wrapper.purge()
        if len(self._backup) > 0:
            for edge in self._backup:
                n = self._wrapper.add_node(edge.n)
                v = self._wrapper.add_node(edge.v)
                self._wrapper.add_edge(n,v,edge)
            self._wrapper.submit()


    def test_full(self):
        self.builder.set_full_view()
        all_edges = self._wrapper.get_all_edges()
        graph = self.builder.view
        view_edges = graph.edges()
        self.assertCountEqual(all_edges,view_edges)
            
    def test_pruned(self):
        self.builder.set_pruned_view()
        graph = self.builder.view
        for edge in graph.edges():
            self.assertTrue(bool(set(edge.get_labels()) & set(str(n) for n in self._wrapper.model.identifiers.predicates)))

    def test_heirarchy(self):
        self.builder.set_hierarchy_view()
        graph = self.builder.view
        for n in graph.nodes():
            actual_children = [c for c in graph.edges(n)]
            expected_children = self.builder.get_children(n)
            self.assertEqual(expected_children, actual_children)

    def test_interaction_explicit(self):
        self.builder.set_interaction_explicit_view()
        graph = self.builder.view
        physical_entity_obj = self._wrapper.model.identifiers.objects.physical_entity
        reaction_entity_obj = self._wrapper.model.identifiers.objects.reaction
        reaction_class_code = self._wrapper.model.get_class_code(reaction_entity_obj)
        pe_class_code = self._wrapper.model.get_class_code(physical_entity_obj)

        for edge in graph.edges():
            n = edge.n
            v = edge.v
            n_type = URIRef(self.builder.get_rdf_type(n)[0].v.get_labels()[0])
            v_type = URIRef(self.builder.get_rdf_type(v)[0].v.get_labels()[0])
            if self._wrapper.model.is_derived(n_type,pe_class_code):
                self.assertTrue(self._wrapper.model.is_derived(v_type,reaction_class_code))
            elif self._wrapper.model.is_derived(n_type,reaction_class_code):
                self.assertTrue(self._wrapper.model.is_derived(v_type,reaction_class_code) or 
                                self._wrapper.model.is_derived(v_type,pe_class_code))
            else:
                self.fail("n is not a physc, inter or react.")

    def test_interaction_verbose(self):
        self.builder.set_interaction_verbose_view()
        graph = self.builder.view
        interaction_obj = self._wrapper.model.identifiers.objects.interaction
        physical_entity_obj = self._wrapper.model.identifiers.objects.physical_entity
        interaction_class_code = self._wrapper.model.get_class_code(interaction_obj)
        pe_class_code = self._wrapper.model.get_class_code(physical_entity_obj)
        interactions_classes = [str(d[1]["key"]) for d in self._wrapper.model.get_derived(interaction_class_code)]
        for edge in graph.edges():
            nt = self.builder.get_rdf_type(edge.n)[0].v.get_labels()
            vt = self.builder.get_rdf_type(edge.v)[0].v.get_labels()
            if bool(set(nt) & set(interactions_classes)):
                self.assertTrue(any(self._wrapper.model.is_derived(URIRef(e_type),pe_class_code) for e_type in vt))

            elif bool(set(vt) & set(interactions_classes)):
                self.assertTrue(any(self._wrapper.model.is_derived(URIRef(e_type),interaction_class_code) for e_type in vt))
            else:
                self.fail("Neither node is an interaction.")
    
    def test_interaction(self):
        self.builder.set_interaction_view()
        graph = self.builder.view
        interaction_obj = self._wrapper.model.identifiers.objects.interaction
        physical_entity_obj = self._wrapper.model.identifiers.objects.physical_entity
        interaction_class_code = self._wrapper.model.get_class_code(interaction_obj)
        pe_class_code = self._wrapper.model.get_class_code(physical_entity_obj)
        interactions_classes = [str(d[1]["key"]) for d in self._wrapper.model.get_derived(interaction_class_code)]
        pe_classes = [str(d[1]["key"]) for d in self._wrapper.model.get_derived(pe_class_code)]
        for edge in graph.edges():
            nt = self.builder.get_rdf_type(edge.n)[0].v.get_labels()
            vt = self.builder.get_rdf_type(edge.v)[0].v.get_labels()
            self.assertTrue(bool(set(edge.get_labels()) & set(interactions_classes)))
            self.assertTrue(bool(set(nt) & set(pe_classes)))
            self.assertTrue(bool(set(vt) & set(pe_classes)))
            
    def test_interaction_genetic(self):
        self.builder.set_interaction_genetic_view()
        graph = self.builder.view
        interaction_obj = self._wrapper.model.identifiers.objects.interaction
        dna_obj = self._wrapper.model.identifiers.objects.dna
        interaction_class_code = self._wrapper.model.get_class_code(interaction_obj)
        dna_class_code = self._wrapper.model.get_class_code(dna_obj)
        interactions_classes = [str(d[1]["key"]) for d in self._wrapper.model.get_derived(interaction_class_code)]
        dna_classes = [str(d[1]["key"]) for d in self._wrapper.model.get_derived(dna_class_code)] + [dna_obj]
        for edge in graph.edges():
            nt = self.builder.get_rdf_type(edge.n)[0].v.get_labels()
            vt = self.builder.get_rdf_type(edge.v)[0].v.get_labels()
            self.assertTrue(bool(set(edge.get_labels()) & set(interactions_classes)))
            self.assertTrue(bool(set(nt) & set(dna_classes)))
            self.assertTrue(bool(set(vt) & set(dna_classes)))

    def test_interaction_protein(self):
        self.builder.set_interaction_protein_view()
        graph = self.builder.view
        interaction_obj = self._wrapper.model.identifiers.objects.interaction
        prot_obj = self._wrapper.model.identifiers.objects.protein
        interaction_class_code = self._wrapper.model.get_class_code(interaction_obj)
        prot_class_code = self._wrapper.model.get_class_code(prot_obj)
        interactions_classes = [str(d[1]["key"]) for d in self._wrapper.model.get_derived(interaction_class_code)]
        protein_classes = [str(prot_obj)] + [str(d[1]["key"]) for d in self._wrapper.model.get_derived(prot_class_code)]
        for edge in graph.edges():
            nt = self.builder.get_rdf_type(edge.n)[0].v.get_labels()
            vt = self.builder.get_rdf_type(edge.v)[0].v.get_labels()
            self.assertTrue(bool(set(edge.get_labels()) & set(interactions_classes)))
            self.assertTrue(bool(set(nt) & set(protein_classes)))
            self.assertTrue(bool(set(vt) & set(protein_classes)))

class TestModes(unittest.TestCase):
    def setUp(self):
        self._wrapper = NVGraph()
        #self._backup = self._wrapper.get_all_edges()
        #self._wrapper.purge()
        #self._wrapper.add_graph(test_fn)
        self.builder = DesignBuilder(self._wrapper)
        #self.builder.set_full_view()

    def tearDown(self):
        return
        self._wrapper.purge()
        if len(self._backup) > 0:
            for edge in self._backup:
                n = self._wrapper.add_node(edge.n)
                v = self._wrapper.add_node(edge.v)
                self._wrapper.add_edge(n,v,edge)
            self._wrapper.submit()
    
    def get_input_graphs(self,fn1,fn2,view_func,mode):
        self._wrapper.purge()
        self._wrapper.add_graph(fn1)
        view_func()
        g1 = self.builder.view
        self._wrapper.purge()
        self._wrapper.add_graph(fn2)
        view_func()
        g2 = self.builder.view
        self._wrapper.add_graph(fn1,mode=mode)
        view_func()
        return g1,g2

    def test_get_tree(self):
        self.builder.set_tree_mode()
        tree_graph = self.builder.view
        for edge in tree_graph.edges():
            print(edge)

    def test_union_identical(self):
        test_fn = os.path.join(curr_dir,"..","files","design","sbol","output.xml")
        self._wrapper.purge()
        self._wrapper.add_graph(test_fn)
        self._wrapper.add_graph(test_fn,mode="duplicate")
        self._wrapper.add_graph(test_fn,mode="merge")
        self.builder.set_full_view()
        pre_nodes = [*self.builder.view.nodes()]
        pre_edges = [*self.builder.view.edges()]
        self.builder.set_union_mode()
        tree_graph = self.builder.view
        post_nodes = [*tree_graph.nodes()]
        post_edges = [*tree_graph.edges()]

        self.assertEqual(len(pre_nodes),len(post_nodes)*2)
        self.assertEqual(len(pre_edges),len(post_edges)*2)
        for node in pre_nodes:
            self.assertIn(node,post_nodes)
        for edge in pre_edges:
            self.assertIn(edge,post_edges)

    def test_union_overlap(self):
        test_fn = os.path.join(curr_dir,"..","files","design","sbol","0x3B.xml")
        test_fn1 = os.path.join(curr_dir,"..","files","design","sbol","0xC7.xml")
        for m in self._wrapper.get_modes():
            self._wrapper.purge()
            self._wrapper.add_graph(test_fn)
            self._wrapper.add_graph(test_fn1,mode=m)
            self.builder.set_interaction_view()
            pre_nodes = [*self.builder.view.nodes()]
            pre_edges = [*self.builder.view.edges()]
            self.builder.set_union_mode()
            tree_graph = self.builder.view
            post_nodes = [*tree_graph.nodes()]
            post_edges = [*tree_graph.edges()]

            for node in pre_nodes:
                self.assertIn(node,post_nodes)
            for edge in pre_edges:
                self.assertIn(edge,post_edges)
            for edge in post_edges:
                self.assertTrue(post_edges.count(edge) == 1)
            for node in post_nodes:
                self.assertTrue(post_nodes.count(node) == 1)

    def test_union_seperate(self):
        test_fn = os.path.join(curr_dir,"..","files","design","sbol","0x3B.xml")
        test_fn1 = os.path.join(curr_dir,"..","files","design","sbol","nor_full.xml")
        self._wrapper.purge()
        self._wrapper.add_graph(test_fn)
        self._wrapper.add_graph(test_fn1,mode="duplicate")
        self.builder.set_interaction_view()
        pre_nodes = [*self.builder.view.nodes()]
        pre_edges = [*self.builder.view.edges()]
        self.builder.set_union_mode()
        tree_graph = self.builder.view
        post_nodes = [*tree_graph.nodes()]
        post_edges = [*tree_graph.edges()]

        self.assertEqual(len(pre_nodes),len(post_nodes))
        self.assertEqual(len(pre_edges),len(post_edges))

        self.assertCountEqual(pre_nodes,post_nodes)
        self.assertCountEqual(pre_edges,post_edges)

    def test_node_intersection_identical(self):
        test_fn = os.path.join(curr_dir,"..","files","design","sbol","output.xml")
        g1,g2 = self.get_input_graphs(test_fn,test_fn,self.builder.set_full_view,"merge")
        pre_nodes = [*self.builder.view.nodes()]
        pre_edges = [*self.builder.view.edges()]
        self.builder.set_edge_intersection_mode()
        view = self.builder.view
        post_nodes = [*view.nodes()]
        post_edges = [*view.edges()]
        self.assertEqual(len(pre_nodes),len(post_nodes))
        self.assertEqual(len(pre_edges),len(post_edges))
        for node in pre_nodes:
            self.assertIn(node,post_nodes)
        for edge in pre_edges:
            self.assertIn(edge,post_edges)

    def test_node_intersection_overlap(self):
        test_fn = os.path.join(curr_dir,"..","files","design","sbol","0x3B.xml")
        test_fn1 = os.path.join(curr_dir,"..","files","design","sbol","0xC7.xml")
        for m in self._wrapper.get_modes():
            g1,g2 = self.get_input_graphs(test_fn,test_fn1,self.builder.set_full_view,m)
            g1_nodes = [*g1.nodes()]
            g2_nodes = [*g2.nodes()]
            pre_nodes = [*self.builder.view.nodes()]
            pre_edges = [*self.builder.view.edges()]
            self.builder.set_full_view()
            self.builder.set_node_intersection_mode()
            view = self.builder.view
            post_nodes = [*view.nodes()]
            post_edges = [*view.edges()]
            for node in post_nodes:
                self.assertIn(node,pre_nodes)
                self.assertTrue(pre_nodes.count(node) == 2 or len(node["graph_name"]) == 2)
                self.assertIn(node,g1_nodes)
                self.assertIn(node,g2_nodes)
            for edge in post_edges:
                self.assertIn(edge,pre_edges)

    def test_node_intersection_seperate(self):
        test_fn = os.path.join(curr_dir,"..","files","design","sbol","0x3B.xml")
        test_fn1 = os.path.join(curr_dir,"..","files","design","sbol","nor_full.xml")
        self._wrapper.purge()
        self._wrapper.add_graph(test_fn)
        self._wrapper.add_graph(test_fn1,mode="duplicate")
        self.builder.set_interaction_view()
        self.builder.set_node_intersection_mode()
        tree_graph = self.builder.view
        post_nodes = [*tree_graph.nodes()]
        post_edges = [*tree_graph.edges()]

        self.assertEqual(len(post_nodes),0)
        self.assertEqual(len(post_edges),0)
        
    def test_edge_intersection_identical(self):
        test_fn = os.path.join(curr_dir,"..","files","design","sbol","output.xml")
        g1,g2 = self.get_input_graphs(test_fn,test_fn,self.builder.set_full_view,"merge")
        pre_nodes = [*self.builder.view.nodes()]
        pre_edges = [*self.builder.view.edges()]
        self.builder.set_edge_intersection_mode()
        view = self.builder.view
        post_nodes = [*view.nodes()]
        post_edges = [*view.edges()]
        self.assertEqual(len(pre_nodes),len(post_nodes))
        self.assertEqual(len(pre_edges),len(post_edges))
        for node in pre_nodes:
            self.assertIn(node,post_nodes)
        for edge in pre_edges:
            self.assertIn(edge,post_edges)

    def test_edge_intersection_overlap(self):
        test_fn = os.path.join(curr_dir,"..","files","design","sbol","0x3B.xml")
        test_fn1 = os.path.join(curr_dir,"..","files","design","sbol","0xC7.xml")
        for m in self._wrapper.get_modes():
            g1,g2 = self.get_input_graphs(test_fn,test_fn1,self.builder.set_full_view,m)
            g1_nodes = [*g1.nodes()]
            g2_nodes = [*g2.nodes()]
            g1_edges = [*g1.edges()]
            g2_edges = [*g2.edges()]
            pre_nodes = [*self.builder.view.nodes()]
            pre_edges = [*self.builder.view.edges()]
            self.builder.set_full_view()
            self.builder.set_edge_intersection_mode()
            view = self.builder.view
            post_nodes = [*view.nodes()]
            post_edges = [*view.edges()]
            for node in post_nodes:
                self.assertIn(node,pre_nodes)
                self.assertTrue(pre_nodes.count(node) == 2 or len(node["graph_name"]) == 2)
                self.assertIn(node,g1_nodes)
                self.assertIn(node,g2_nodes)
            for edge in post_edges:
                self.assertIn(edge,pre_edges)
                self.assertTrue(pre_edges.count(edge) == 2 or len(edge["graph_name"]) == 2)
                self.assertIn(edge,g1_edges)
                self.assertIn(edge,g2_edges)

    def test_edge_intersection_seperate(self):
        test_fn = os.path.join(curr_dir,"..","files","design","sbol","0x3B.xml")
        test_fn1 = os.path.join(curr_dir,"..","files","design","sbol","nor_full.xml")
        self._wrapper.purge()
        self._wrapper.add_graph(test_fn)
        self._wrapper.add_graph(test_fn1,mode="duplicate")
        self.builder.set_interaction_view()
        self.builder.set_edge_intersection_mode()
        tree_graph = self.builder.view
        post_nodes = [*tree_graph.nodes()]
        post_edges = [*tree_graph.edges()]

        self.assertEqual(len(post_nodes),0)
        self.assertEqual(len(post_edges),0)
        
    def test_node_difference_identical(self):
        test_fn = os.path.join(curr_dir,"..","files","design","sbol","output.xml")
        self._wrapper.purge()
        self._wrapper.add_graph(test_fn)
        self._wrapper.add_graph(test_fn,mode="duplicate")
        self.builder.set_full_view()
        self.builder.set_node_difference_mode()
        tree_graph = self.builder.view
        post_nodes = [*tree_graph.nodes()]
        post_edges = [*tree_graph.edges()]

        self.assertEqual(len(post_nodes),0)
        self.assertEqual(len(post_edges),0)

    def test_node_difference_overlap(self):
        test_fn = os.path.join(curr_dir,"..","files","design","sbol","0x3B.xml")
        test_fn1 = os.path.join(curr_dir,"..","files","design","sbol","0xC7.xml")
        for m in self._wrapper.get_modes():
            g1,g2 = self.get_input_graphs(test_fn,test_fn1,self.builder.set_full_view,m)
            g1_nodes = [*g1.nodes()]
            g2_nodes = [*g2.nodes()]
            pre_nodes = [*self.builder.view.nodes()]
            pre_edges = [*self.builder.view.edges()]
            self.builder.set_full_view()
            self.builder.set_node_difference_mode()
            view = self.builder.view
            post_nodes = [*view.nodes()]
            post_edges = [*view.edges()]
            for node in post_nodes:
                self.assertIn(node,pre_nodes)
                if m != "ignore" and m != "overwrite": 
                    self.assertTrue(bool(node in g1_nodes) != bool(node in g2_nodes)) #XOR
                self.assertTrue(pre_nodes.count(node) == 1  or len(node["graph_name"]) == 1)
            for edge in post_edges:
                self.assertIn(edge,pre_edges)

    def test_node_difference_seperate(self):
        test_fn = os.path.join(curr_dir,"..","files","design","sbol","0x3B.xml")
        test_fn1 = os.path.join(curr_dir,"..","files","design","sbol","nor_full.xml")
        self._wrapper.purge()
        self._wrapper.add_graph(test_fn)
        self._wrapper.add_graph(test_fn1,mode="duplicate")
        self.builder.set_interaction_view()
        self.builder.set_node_intersection_mode()
        tree_graph = self.builder.view
        post_nodes = [*tree_graph.nodes()]
        post_edges = [*tree_graph.edges()]

        self.assertEqual(len(post_nodes),0)
        self.assertEqual(len(post_edges),0)
        
    def test_edge_difference_identical(self):
        test_fn = os.path.join(curr_dir,"..","files","design","sbol","output.xml")
        self._wrapper.purge()
        self._wrapper.add_graph(test_fn)
        self._wrapper.add_graph(test_fn,mode="duplicate")
        self.builder.set_full_view()
        pre_nodes = [*self.builder.view.nodes()]
        pre_edges = [*self.builder.view.edges()]
        self.builder.set_edge_intersection_mode()
        tree_graph = self.builder.view
        post_nodes = [*tree_graph.nodes()]
        post_edges = [*tree_graph.edges()]

        self.assertEqual(len(pre_nodes),len(post_nodes)*2)
        self.assertEqual(len(pre_edges),len(post_edges)*2)
        for node in pre_nodes:
            self.assertIn(node,post_nodes)
        for edge in pre_edges:
            self.assertIn(edge,post_edges)

    def test_edge_difference_overlap(self):
        test_fn = os.path.join(curr_dir,"..","files","design","sbol","0x3B.xml")
        test_fn1 = os.path.join(curr_dir,"..","files","design","sbol","0xC7.xml")
        for m in self._wrapper.get_modes():
            g1,g2 = self.get_input_graphs(test_fn,test_fn1,self.builder.set_full_view,m)
            g1_nodes = [*g1.nodes()]
            g2_nodes = [*g2.nodes()]
            g1_edges = [*g1.edges()]
            g2_edges = [*g2.edges()]
            pre_nodes = [*self.builder.view.nodes()]
            pre_edges = [*self.builder.view.edges()]
            self.builder.set_full_view()
            self.builder.set_node_difference_mode()
            view = self.builder.view
            post_nodes = [*view.nodes()]
            post_edges = [*view.edges()]
            for node in post_nodes:
                self.assertIn(node,pre_nodes)
                self.assertTrue(pre_nodes.count(node) == 1)
                if m != "ignore" and m != "overwrite": 
                    # Doesnt make sense with this setting as it ignores duplicates 
                    # when adding graph so there is no way of knowing if the second graph has elements from first graph.
                    self.assertTrue(bool(node in g1_nodes) != bool(node in g2_nodes)) #XOR
                self.assertTrue(pre_nodes.count(node) == 1  or len(node["graph_name"]) == 1)
            for edge in post_edges:
                self.assertIn(edge,pre_edges)
                self.assertTrue(pre_edges.count(edge) == 1)
                if m != "ignore" and m != "overwrite": 
                    # Doesnt make sense with this setting as it ignores duplicates 
                    # when adding graph so there is no way of knowing if the second graph has elements from first graph.
                    self.assertTrue(bool(edge in g1_edges) != bool(edge in g2_edges)) #XOR
                self.assertTrue(pre_edges.count(edge) == 1  or len(edge["graph_name"]) == 1)

    def test_edge_difference_seperate(self):
        test_fn = os.path.join(curr_dir,"..","files","design","sbol","0x3B.xml")
        test_fn1 = os.path.join(curr_dir,"..","files","design","sbol","nor_full.xml")
        self._wrapper.purge()
        self._wrapper.add_graph(test_fn)
        self._wrapper.add_graph(test_fn1,mode="duplicate")
        self.builder.set_interaction_view()
        self.builder.set_edge_intersection_mode()
        tree_graph = self.builder.view
        post_nodes = [*tree_graph.nodes()]
        post_edges = [*tree_graph.edges()]

        self.assertEqual(len(post_nodes),0)
        self.assertEqual(len(post_edges),0)

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
