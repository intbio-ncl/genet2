import unittest
import os
import sys
from rdflib import URIRef

sys.path.insert(0, os.path.join(".."))
sys.path.insert(0, os.path.join("..",".."))
sys.path.insert(0, os.path.join("..","..",".."))

from app.visualiser.builder.projection import ProjectionBuilder
from app.graph.world_graph import WorldGraph
from  app.graph.utility.model.model import model

curr_dir = os.path.dirname(os.path.realpath(__file__))
test_fn = os.path.join(curr_dir,"..","files","nor_full.xml")


class TestViews(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.gn = "test_builder_views"
        self.wg = WorldGraph()
        self.dg = self.wg.add_design(test_fn,self.gn)
        self.all_nodes = self.dg.nodes()
        self.all_edges = self.dg.edges()
        self.builder = ProjectionBuilder(self.wg)
        self.builder.set_design(self.dg)

    @classmethod
    def tearDownClass(self):
        self.wg.remove_design(self.gn)
    
    def tearDown(self):
        self.builder.set_design(self.dg)

    def test_projection_hierarchy(self):
        pgn = "test_projection_hierarchy"
        try:
            self.wg.driver.project.drop(pgn)
        except Exception as ex:
            pass

        hp = model.identifiers.predicates.hasPart
        physical_entity_obj = model.identifiers.objects.physical_entity
        pe_class_code = model.get_class_code(physical_entity_obj)
        pe_classes = [str(d[1]["key"]) for d in model.get_derived(pe_class_code)]

        self.builder.project_preset(pgn,"hierarchy")
        self.builder.set_projection_view(pgn)
        graph = self.builder.view
        view_edges = graph.edges()
        for e in view_edges:
            self.assertIn(e.n.get_type(),pe_classes)
            self.assertIn(e.v.get_type(),pe_classes)
            self.assertEqual(e.get_type(),str(hp))

    def test_projection_interaction(self):
        pgn = "test_projection_interaction"
        try:
            self.wg.driver.project.drop(pgn)
        except Exception as ex:
            pass

        hp = model.identifiers.predicates.hasPart
        physical_entity_obj = model.identifiers.objects.physical_entity
        interaction_obj = model.identifiers.objects.interaction
        pe_class_code = model.get_class_code(physical_entity_obj)
        pe_classes = [str(d[1]["key"]) for d in model.get_derived(pe_class_code)]
        interaction_class_code = model.get_class_code(interaction_obj)
        int_classes = [str(d[1]["key"]) for d in model.get_derived(interaction_class_code)]
        ips = [str(s[1]["key"]) for s in model.interaction_predicates()]

        self.builder.project_preset(pgn,"interaction",direction="NATURAL",type="bipartite")
        self.builder.set_projection_view(pgn)
        graph = self.builder.view
        view_edges = graph.edges()
        for e in view_edges:
            self.assertIn(e.v.get_type(),pe_classes)
            self.assertIn(e.n.get_type(),int_classes)
            self.assertIn(e.get_type(),ips)
        self.wg.driver.project.drop(pgn)

        self.builder.project_preset(pgn,"interaction",direction="DIRECTED",type="bipartite")
        self.builder.set_projection_view(pgn)
        graph = self.builder.view
        view_edges = graph.edges()
        for e in view_edges:
            self.assertIn(e.v.get_type(),pe_classes + int_classes)
            self.assertIn(e.n.get_type(),int_classes + pe_classes)
            self.assertIn(e.get_type(),ips)
        self.wg.driver.project.drop(pgn)

        self.builder.project_preset(pgn,"interaction",direction="UNDIRECTED",type="bipartite")
        self.builder.set_projection_view(pgn)
        graph = self.builder.view
        view_edges = graph.edges()
        for e in view_edges:
            self.assertIn(e.v.get_type(),pe_classes + int_classes)
            self.assertIn(e.n.get_type(),int_classes + pe_classes)
            self.assertIn(e.get_type(),ips)
        self.wg.driver.project.drop(pgn)

        self.builder.project_preset(pgn,"interaction",direction="NATURAL",type="monopartite")
        self.builder.set_projection_view(pgn)
        graph = self.builder.view
        view_edges = list(graph.edges())
        self.assertEqual(len(view_edges),0)
        self.wg.driver.project.drop(pgn)

        self.builder.project_preset(pgn,"interaction",direction="DIRECTED",type="monopartite")
        self.builder.set_projection_view(pgn)
        graph = self.builder.view
        view_edges = graph.edges()
        for e in view_edges:
            self.assertIn(e.v.get_type(),pe_classes)
            self.assertIn(e.n.get_type(),pe_classes)
            self.assertIn(e.get_type(),int_classes)
        self.wg.driver.project.drop(pgn)

        self.builder.project_preset(pgn,"interaction",direction="UNDIRECTED",type="monopartite")
        self.builder.set_projection_view(pgn)
        graph = self.builder.view
        view_edges = graph.edges()
        for e in view_edges:
            self.assertIn(e.v.get_type(),pe_classes)
            self.assertIn(e.n.get_type(),pe_classes)
            self.assertIn(e.get_type(),int_classes)
        self.wg.driver.project.drop(pgn)

    def test_projection_interaction_ppi(self):
        pgn = "test_projection_interaction_ppi"
        try:
            self.wg.driver.project.drop(pgn)
        except Exception as ex:
            pass

        protein_c = model.identifiers.objects.protein
        interaction_obj = model.identifiers.objects.interaction
        pe_class_code = model.get_class_code(protein_c)
        pe_classes = [str(protein_c)] + [str(d[1]["key"]) for d in model.get_derived(pe_class_code)]
        interaction_class_code = model.get_class_code(interaction_obj)
        int_classes = [str(d[1]["key"]) for d in model.get_derived(interaction_class_code)]

        self.builder.project_preset(pgn,"interaction_ppi",direction="DIRECTED")
        self.builder.set_projection_view(pgn)
        graph = self.builder.view
        view_edges = graph.edges()
        for e in view_edges:
            self.assertIn(e.v.get_type(),pe_classes)
            self.assertIn(e.n.get_type(),pe_classes)
            self.assertIn(e.get_type(),int_classes)
        self.wg.driver.project.drop(pgn)

        self.builder.project_preset(pgn,"interaction_ppi",direction="UNDIRECTED")
        self.builder.set_projection_view(pgn)
        graph = self.builder.view
        view_edges = graph.edges()
        for e in view_edges:
            self.assertIn(e.v.get_type(),pe_classes)
            self.assertIn(e.n.get_type(),pe_classes)
            self.assertIn(e.get_type(),int_classes)
        self.wg.driver.project.drop(pgn)

    def test_projection_interaction_genetic(self):
        pgn = "test_projection_interaction_genetic"
        try:
            self.wg.driver.project.drop(pgn)
        except Exception as ex:
            pass

        protein_c = model.identifiers.objects.dna
        interaction_obj = model.identifiers.objects.interaction
        pe_class_code = model.get_class_code(protein_c)
        pe_classes = [str(protein_c)] + [str(d[1]["key"]) for d in model.get_derived(pe_class_code)]
        interaction_class_code = model.get_class_code(interaction_obj)
        int_classes = [str(d[1]["key"]) for d in model.get_derived(interaction_class_code)]

        self.builder.project_preset(pgn,"interaction_genetic",direction="DIRECTED")
        self.builder.set_projection_view(pgn)
        graph = self.builder.view
        view_edges = graph.edges()
        for e in view_edges:
            self.assertIn(e.v.get_type(),pe_classes)
            self.assertIn(e.n.get_type(),pe_classes)
            self.assertIn(e.get_type(),int_classes)
        self.wg.driver.project.drop(pgn)

        self.builder.project_preset(pgn,"interaction_genetic",direction="UNDIRECTED")
        self.builder.set_projection_view(pgn)
        graph = self.builder.view
        view_edges = graph.edges()
        for e in view_edges:
            self.assertIn(e.v.get_type(),pe_classes)
            self.assertIn(e.n.get_type(),pe_classes)
            self.assertIn(e.get_type(),int_classes)
        self.wg.driver.project.drop(pgn)
        
if __name__ == '__main__':
    unittest.main()
