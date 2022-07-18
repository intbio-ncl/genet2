import unittest
import os
import sys
from rdflib import RDF,URIRef
sys.path.insert(0, os.path.join(".."))
sys.path.insert(0, os.path.join("..",".."))
sys.path.insert(0, os.path.join("..","..",".."))

from app.visualiser.builder.editor import EditorBuilder
from app.graph.world_graph import WorldGraph
from  app.graph.utility.model.model import model
from app.graph.utility.graph_objects.node import Node

curr_dir = os.path.dirname(os.path.realpath(__file__))
test_fn = os.path.join(curr_dir,"..","files","nor_full.xml")

class TestEditor(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.gn = "test_builder_views"
        self.wg = WorldGraph()
        self.wg.remove_design(self.gn)
        self.dg = self.wg.get_design(self.gn,"ANY")
        self.dg = self.wg.add_design(test_fn,self.gn)
        self.builder = EditorBuilder(self.wg)
        self.builder.set_design(self.dg)

    @classmethod
    def tearDownClass(self):
        self.wg.remove_design(self.gn)
    
    def test_add_node(self):
        key = "test_add_node/test_add_node"
        ntype = model.identifiers.objects.DNA
        self.builder.add_node(key,ntype)
        res = self.dg.nodes(key)
        self.assertTrue(len(res)==1)
        self.assertEqual(res[0].get_key(),key)
        
        self.wg.driver.remove_node(res[0])
        self.wg.driver.submit()
        res = self.dg.nodes(res[0])
        self.assertTrue(len(res)==0)

    def test_get_io_nodes(self):
        self.builder.set_full_view()
        self.builder.build()
        ips = [k[1]["key"] for k in model.interaction_predicates()]
        ccc = model.get_class_code(model.identifiers.objects.conceptual_entity)
        pee = model.get_class_code(model.identifiers.objects.physical_entity)
        for pred in ips:
            inps,outs = self.builder.get_io_nodes(pred)
            for name,ins in inps.items():
                self.assertEqual(name,"subject")
                for i in ins:
                    self.assertTrue(model.is_derived(URIRef(i.get_type()),ccc))
            for name,out in outs.items():
                self.assertEqual(name,"object")
                for o in out:
                    self.assertTrue(model.is_derived(URIRef(o.get_type()),pee))
    
    def test_get_io_nodes_interaction(self):
        self.builder.set_full_view()
        self.builder.build()
        icc = model.get_class_code(model.identifiers.objects.interaction)
        pee = model.get_class_code(model.identifiers.objects.physical_entity)
        ip = [str(k[1]["key"]) for k in model.interaction_predicates()]
        io = [k[1]["key"] for k in model.get_derived(icc)]
        for i in io:
            inps,outs = self.builder.get_io_nodes(i)
            for name,ins in inps.items():
                self.assertIn(name,ip)
                for i in ins:
                    self.assertTrue(model.is_derived(URIRef(i.get_type()),pee))
            for name,out in outs.items():
                self.assertIn(name,ip)
                for o in out:
                    self.assertTrue(model.is_derived(URIRef(o.get_type()),pee))

    def test_add_edges_full(self):
        self.builder.set_full_view()
        self.builder.build()
        nodes = self.builder.get_view_nodes()
        node1 = nodes[0]
        node2 = nodes[1]
        n = {"subject" : node1}
        v = {"object" : node2}
        e = self.builder.get_view_edge_types()[0]
        self.builder.add_edges(n,v,e)

        res = self.dg.edges(node1,node2,e)
        self.assertTrue(len(res)==1)
        self.assertEqual(res[0].n.get_key(),node1.get_key())
        self.assertEqual(res[0].v.get_key(),node2.get_key())
        self.assertEqual(res[0].get_type(),e)
        
        self.wg.driver.remove_edge(res[0])
        self.wg.driver.submit()
        res = self.dg.edges(node1,node2,e)
        self.assertTrue(len(res)==0)

    def test_add_edges_pruned(self):
        from app.visualiser.builder.builders.design.pruned import bl_pred
        self.builder.set_pruned_view()
        self.builder.build()
        nodes = self.builder.get_view_nodes()
        node1 = nodes[0]
        node2 = nodes[1]
        n = {"subject" : node1}
        v = {"object" : node2}
        e = self.builder.get_view_edge_types()[0]
        self.builder.add_edges(n,v,e)
        res = self.dg.edges(node1,node2,e)
        self.assertTrue(len(res)==1)
        self.assertEqual(res[0].n.get_key(),node1.get_key())
        self.assertEqual(res[0].v.get_key(),node2.get_key())
        self.assertEqual(res[0].get_type(),e)

        self.wg.driver.remove_edge(res[0])
        self.wg.driver.submit()
        res = self.dg.edges(node1,node2,e)
        self.assertTrue(len(res)==0)

        e = list(bl_pred)[0]
        res = self.dg.edges(node1,node2,e)
        self.assertTrue(len(res)==0)
        
    def test_add_edges_hierarchy(self):
        self.builder.set_hierarchy_view()
        self.builder.build()
        nodes = self.builder.get_view_nodes()
        proteins = self.builder._dg.get_protein()
        node1 = nodes[0]
        node2 = nodes[1]
        n = {"subject" : node1}
        v = {"object" : node2}
        e = model.identifiers.predicates.has_part
        self.builder.add_edges(n,v,e)        
        res = self.dg.edges(node1,node2,e)
        self.assertTrue(len(res)==1)
        self.assertEqual(res[0].n.get_key(),node1.get_key())
        self.assertEqual(res[0].v.get_key(),node2.get_key())
        self.assertEqual(res[0].get_type(),str(e))
        self.wg.driver.remove_edge(res[0])
        self.wg.driver.submit()
        res = self.dg.edges(node1,node2,e)
        self.assertTrue(len(res)==0)

        node1 = proteins[0]
        node2 = proteins[1]
        n = {"subject" : node1}
        v = {"object" : node2}
        e = model.identifiers.predicates.has_sequence
        self.builder.add_edges(n,v,e)        
        res = self.dg.edges(node1,node2,e)
        self.assertTrue(len(res)==0)

    def test_add_edges_interaction_verbose(self):
        self.builder.set_interaction_verbose_view()
        self.builder.build()

        node1 = self.dg.get_interaction()[0]
        node2 = self.dg.get_physicalentity()[0]
        n = {"subject" : node1}
        v = {"object" : node2}
        e = self.builder.get_view_edge_types()[0]
        self.builder.add_edges(n,v,e)        
        res = self.dg.edges(node1,node2,e)
        self.assertTrue(len(res)==1)
        self.assertEqual(res[0].n.get_key(),node1.get_key())
        self.assertEqual(res[0].v.get_key(),node2.get_key())
        self.assertEqual(res[0].get_type(),str(e))
        self.wg.driver.remove_edge(res[0])
        self.wg.driver.submit()
        res = self.dg.edges(node1,node2,e)
        self.assertTrue(len(res)==0)

        node1,node2 = node2,node1
        n = {"subject" : node1}
        v = {"object" : node2}
        self.builder.add_edges(n,v,e)        
        res = self.dg.edges(node1,node2,e)
        self.assertTrue(len(res)==0)

    def test_add_edges_interaction(self):
        self.builder.set_interaction_view()
        self.builder.build()
        pe = self.dg.get_physicalentity()
        node1 = pe[0]
        node2 = pe[1]
        e = self.builder.get_view_edge_types()[0]
        inps,outs = model.interaction_predicates(model.get_class_code(e))
        n = {inps[0][1]["key"] : node1}
        v = {outs[0][1]["key"] : node2}

        pre_res = self.dg.edges(v=node1)
        self.builder.add_edges(n,v,e)        
        res = self.dg.edges(v=node1)
        res = list(set(res) - set(pre_res))
        self.assertTrue(len(res)==1)
        self.wg.driver.remove_node(res[0].n)
        self.wg.driver.remove_edge(res[0])
        self.wg.driver.submit()
        res = self.dg.edges(res[0].n)

        node1,node2 = node2,node1
        n = {"subject" : node1}
        v = {"object" : node2}
        self.builder.add_edges(n,v,e)        
        res = self.dg.edges(v=node1,e=e)
        self.assertTrue(len(res)==0)

    def test_add_edges_interaction_conversion(self):
        self.builder.set_interaction_view()
        self.builder.build()
        pe = self.dg.get_physicalentity()
        node1 = pe[0]
        node2 = pe[1]
        node3 = pe[2]
        e = str(model.identifiers.objects.Conversion)
        inps,outs = model.interaction_predicates(model.get_class_code(e))
        n = {inps[0][1]["key"] : node1,inps[1][1]["key"] : node3}
        v = {outs[0][1]["key"] : node2}

        pre_res = self.dg.edges(v=node1)
        self.builder.add_edges(n,v,e)        
        res = self.dg.edges(v=node1)
        res = list(set(res) - set(pre_res))
        self.assertTrue(len(res)==1)
        self.wg.driver.remove_node(res[0].n)
        self.wg.driver.remove_edge(res[0])
        self.wg.driver.submit()
        res = self.dg.edges(res[0].n)

    def test_add_edges_interaction_advanced(self):
        gn = "test_interaction_advanced"
        fn = os.path.join(curr_dir,"..","files","two_nodes_interaction.xml")
        self.wg.remove_design(gn)
        dg = self.wg.add_design(fn,gn)
        self.builder.set_design(dg)
        pe = dg.get_physicalentity()
        ints = dg.get_interaction()

        self.builder.set_interaction_view()
        self.builder.build()

        # Already present edge.
        node1 = pe[0]
        node2 = pe[1]
        e = self.builder.get_view_edge_types()[0]
        inps,outs = model.interaction_predicates(model.get_class_code(e))
        n = {inps[0][1]["key"] : node1}
        v = {outs[0][1]["key"] : node2}
        e = ints[0]

        pre_res = self.dg.edges()
        self.builder.add_edges(n,v,e)        
        res = self.dg.edges()
        res = list(set(res) - set(pre_res))
        self.assertTrue(len(res)==0)

        # A Node not in the graph.
        node3 = Node("https:/test.org/testpe",str(model.identifiers.objects.dna))
        e = str(model.identifiers.objects.Conversion)
        inps,outs = model.interaction_predicates(model.get_class_code(e))
        n = {inps[0][1]["key"] : node1,inps[1][1]["key"] : node3}
        v = {outs[0][1]["key"] : node2}

        self.builder.add_edges(n,v,e)        
        res = dg.edges(v=node3)
        self.assertTrue(len(res)==1)
        self.assertEqual(res[0].get_type(),str(inps[1][1]["key"]))
        self.wg.remove_design(gn)

    def test_add_edges_interaction_protein(self):
        self.builder.set_interaction_protein_view()
        self.builder.build()
        pe = self.dg.get_protein()
        node1 = pe[0]
        node2 = pe[1]
        e = self.builder.get_view_edge_types()[0]
        inps,outs = model.interaction_predicates(model.get_class_code(e))
        n = {str(inps[0][1]["key"]) : node1}
        v = {str(outs[0][1]["key"]) : node2}
        pre_res = self.dg.edges()
        self.builder.add_edges(n,v,e)
        res = self.dg.edges()
        new_edges = list(set(res) - set(pre_res))
        self.assertTrue(len(new_edges) == 5)
        nodes = []
        for edge in new_edges:
            nodes += [edge.n,edge.v]
        self.assertIn(node1,nodes)
        self.assertNotIn(node2,nodes)

        pre_res = self.dg.edges()
        self.builder.add_edges(n,v,e)
        res = self.dg.edges()
        res = list(set(res) - set(pre_res))
        self.assertTrue(len(res) == 0)

        for r in new_edges:
            self.wg.driver.remove_edge(r)
        self.wg.driver.submit()

    def test_add_edges_interaction_genetic_dna(self):
        self.builder.set_interaction_genetic_view()
        self.builder.build()
        node1 = Node("www.test.org/PsuedoNode1",model.identifiers.objects.dna)
        node2 = Node("www.test.org/PsuedoNode2",model.identifiers.objects.dna)
        self.builder.add_node(node1.get_key(),node1.get_type())
        self.builder.add_node(node2.get_key(),node2.get_type())
        e = self.builder.get_view_edge_types()[0]
        inps,outs = model.interaction_predicates(model.get_class_code(e))
        n = {str(inps[0][1]["key"]) : node1}
        v = {str(outs[0][1]["key"]) : node2}
        pre_res = self.dg.edges()
        self.builder.add_edges(n,v,e)
        res = self.dg.edges()
        new_edges = list(set(res) - set(pre_res))
        self.assertTrue(len(new_edges) == 5)        
        pre_res = self.dg.edges()
        self.builder.add_edges(n,v,e)
        res = self.dg.edges()
        res = list(set(res) - set(pre_res))
        self.assertTrue(len(res) == 0)
        for r in new_edges:
            self.wg.driver.remove_edge(r)
        self.wg.driver.submit()

    def test_add_edges_interaction_genetic_pac(self):
        self.builder.set_interaction_genetic_view()
        self.builder.build()
        node1 = self.get_node(model.identifiers.objects.promoter)
        node2 = self.get_node(model.identifiers.objects.cds)
        self.builder.add_node(node1.get_key(),node1.get_type())
        self.builder.add_node(node2.get_key(),node2.get_type())
        e = str(model.identifiers.objects.activation)
        inps,outs = model.interaction_predicates(model.get_class_code(e))
        n = {str(inps[0][1]["key"]) : node1}
        v = {str(outs[0][1]["key"]) : node2}
        pre_res = self.dg.edges()
        self.builder.add_edges(n,v,e)
        res = self.dg.edges()
        new_edges = list(set(res) - set(pre_res))
        self.assertTrue(len(new_edges) == 5)        
        pre_res = self.dg.edges()
        self.builder.add_edges(n,v,e)
        res = self.dg.edges()
        res = list(set(res) - set(pre_res))
        self.assertTrue(len(res) == 0)
        for r in new_edges:
            self.wg.driver.remove_edge(r)
        self.wg.driver.submit()

    def test_add_edges_interaction_genetic_prp(self):
        self.builder.set_interaction_genetic_view()
        self.builder.build()
        node1 = self.get_node(model.identifiers.objects.promoter,True)
        node2 = self.get_node(model.identifiers.objects.promoter)
        self.builder.add_node(node1.get_key(),node1.get_type())
        self.builder.add_node(node2.get_key(),node2.get_type())
        e = str(model.identifiers.objects.repression)
        inps,outs = model.interaction_predicates(model.get_class_code(e))
        n = {str(inps[0][1]["key"]) : node1}
        v = {str(outs[0][1]["key"]) : node2}
        pre_res = self.dg.edges()
        self.builder.add_edges(n,v,e)
        res = self.dg.edges()
        new_edges = list(set(res) - set(pre_res))
        self.assertTrue(len(new_edges) == 10,len(new_edges))        
        pre_res = self.dg.edges()
        self.builder.add_edges(n,v,e)
        res = self.dg.edges()
        res = list(set(res) - set(pre_res))
        self.assertTrue(len(res) == 0)
        for r in new_edges:
            self.wg.driver.remove_edge(r)
        self.wg.driver.submit()

    def test_add_edges_interaction_genetic_prp_no_protein(self):
        self.builder.set_interaction_genetic_view()
        self.builder.build()
        self.builder._dg.remove_node(Node(model.identifiers.objects.protein))
        self.builder._dg.remove_node(Node(model.identifiers.objects.genetic_production))
        node1 = self.get_node(model.identifiers.objects.promoter,True)
        node2 = self.get_node(model.identifiers.objects.promoter)
        self.builder.add_node(node1.get_key(),node1.get_type())
        self.builder.add_node(node2.get_key(),node2.get_type())
        e = str(model.identifiers.objects.repression)
        inps,outs = model.interaction_predicates(model.get_class_code(e))
        n = {str(inps[0][1]["key"]) : node1}
        v = {str(outs[0][1]["key"]) : node2}
        pre_res = self.dg.edges()
        self.builder.add_edges(n,v,e)
        res = self.dg.edges()
        new_edges = list(set(res) - set(pre_res))
        self.assertTrue(len(new_edges) == 36,len(new_edges))        
        pre_res = self.dg.edges()
        self.builder.add_edges(n,v,e)
        res = self.dg.edges()
        res = list(set(res) - set(pre_res))
        self.assertTrue(len(res) == 0)
        for r in new_edges:
            self.wg.driver.remove_edge(r)
        self.wg.driver.submit()

    def get_node(self,n_type,use_second=False):
        for n in self.builder.view.nodes():
            if n.get_type() == str(n_type):
                if use_second:
                    use_second = False
                    continue
                return n

if __name__ == '__main__':
    unittest.main()
