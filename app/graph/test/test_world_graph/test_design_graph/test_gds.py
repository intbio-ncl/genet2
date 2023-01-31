import sys
import os
import unittest

sys.path.insert(0, os.path.join(".."))
sys.path.insert(0, os.path.join("..",".."))
sys.path.insert(0, os.path.join("..","..",".."))
sys.path.insert(0, os.path.join("..","..","..",".."))
sys.path.insert(0, os.path.join("..","..","..","..",".."))
from world_graph import WorldGraph
from graph.utility.model.model import model
from converter.sbol_convert import convert
curr_dir = os.path.dirname(os.path.realpath(__file__))

fn = os.path.join(curr_dir,"..","..","files","nor_full.xml")
class TestDesignGraphGDS(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.gn = "TestDesignGraphGDS"
        self.wg = WorldGraph()
        convert(fn,self.wg.driver,self.gn)
        self.dg = self.wg.get_design(self.gn)

    @classmethod
    def tearDownClass(self):
        pass#self.wg.remove_design(self.gn)

    # Interaction
    def test_interaction_direction(self):
        p_name = "test_interaction_direction"
        try:
            self.dg.driver.project.drop(p_name)
        except ValueError:
            pass

        predicates = [str(k[1]["key"]) for k in model.interaction_predicates()]
        ints = self.dg.get_interaction()
        pes = self.dg.get_physicalentity()
        entity = [k.get_key() for k in ints] + [p.get_key() for p in pes]
        graph,interactions,pet = self.dg.project._interaction_direction(p_name,"DIRECTED")
        gi = graph._graph_info()
        config = gi["configuration"]
        rp = config["relationshipProjection"]
        np = config["nodeProjection"]
        for k,v in rp.items():
            self.assertIn(k,predicates)
        for k,v in np.items():
            self.assertIn(k,entity)
        for interaction,(i,o) in interactions.items():
            self.assertTrue(interaction in ints)
            for inp in i:
                self.assertIn(inp.n.get_key(),entity)
                self.assertIn(inp.v.get_key(),entity)
                self.assertIn(inp.get_type(),predicates)
            for out in o:
                self.assertIn(out.n.get_key(),entity)
                self.assertIn(out.v.get_key(),entity)
                self.assertIn(out.get_type(),predicates)

    def test_interaction_natural_bipartite(self):
        ids = model.identifiers
        ips = [str(i[1]["key"]) for i in model.interaction_predicates()]
        pe = ids.objects.physical_entity
        gn = "test1"
        try:
            self.dg.driver.project.drop(gn)
        except ValueError:
            pass
        direction = "NATURAL"
        res = self.dg.project.interaction(gn,direction=direction,type="bipartite")
        self.assertEqual(gn,res.name())

        gi = res._graph_info()
        config = gi["configuration"]

        rp = config["relationshipProjection"]
        for k,v in rp.items():
            self.assertIn(k,ips)
            self.assertEqual(v["orientation"],direction)
        
        np = config["nodeProjection"]
        pis = ([k.get_key() for k in self.dg.get_physicalentity()] + 
               [k.get_type() for k in self.dg.get_physicalentity()] + 
              [k.get_key() for k in self.dg.get_interaction()])
        for k,v in np.items():
            self.assertIn(k,pis)
        self.dg.driver.project.drop(gn)

    def test_interaction_directed_bipartite(self):
        ids = model.identifiers
        interaction = ids.objects.interaction
        pe = ids.objects.physical_entity
        gn = "test1"
        try:
            self.dg.driver.project.drop(gn)
        except ValueError:
            pass

        direction = "DIRECTED"
        res = self.dg.project.interaction(gn,direction=direction,type="bipartite")
        self.assertEqual(gn,res.name())
        int_der = [str(n[1]["key"]) for n in model.get_derived(interaction)]
        pe_der = [str(n[1]["key"]) for n in model.get_derived(pe)]
        ip = [str(n[1]["key"]) for n in model.interaction_predicates()]
        ge = res._graph_info()
        relationship_projection = ge["configuration"]["relationshipProjection"]
        for k,v in relationship_projection.items():
            if "Input" in model.get_interaction_direction(model.get_class_code(k))[0][1]["key"]:
                self.assertEqual(v["orientation"],"REVERSE")
            else:
                self.assertEqual(v["orientation"],"NATURAL")

        schema = ge["schema"]
        edges = schema["relationships"].keys()
        nodes = schema["nodes"].keys()
        pe_der += [n.get_key() for n in self.dg.driver.node_query(list(nodes))]
        for e in edges:
            self.assertIn(e,ip)
        for n in nodes:            
            self.assertIn(n,pe_der+int_der)
        self.dg.driver.project.drop(gn)

    def test_interaction_undirected_bipartite(self):
        ids = model.identifiers
        interaction = ids.objects.interaction
        pe = ids.objects.physical_entity
        gn = "test1"
        try:
            self.dg.driver.project.drop(gn)
        except ValueError:
            pass

        direction = "UNDIRECTED"
        res = self.dg.project.interaction(gn,direction=direction,type="bipartite")
        self.assertEqual(gn,res.name())
        int_der = [str(n[1]["key"]) for n in model.get_derived(interaction)]
        pe_der = [str(n[1]["key"]) for n in model.get_derived(pe)]
        ip = [str(n[1]["key"]) for n in model.interaction_predicates()]
        ge = res._graph_info()
        relationship_projection = ge["configuration"]["relationshipProjection"]
        for k,v in relationship_projection.items():
            self.assertEqual(v["orientation"],"UNDIRECTED")

        schema = ge["schema"]
        edges = schema["relationships"].keys()
        nodes = schema["nodes"].keys()
        pe_der += [n.get_key() for n in self.dg.driver.node_query(list(nodes))]
        for e in edges:
            self.assertIn(e,ip)
        for n in nodes:            
            self.assertIn(n,pe_der+int_der)
        self.dg.driver.project.drop(gn)
    
    def test_interaction_natural_monpartite(self):
        gn = "test1"
        try:
            self.dg.driver.project.drop(gn)
        except ValueError:
            pass
        res = self.dg.project.interaction(gn,direction="NATURAL",type="monopartite")
        self.assertEqual(gn,res.name())
        self.assertEqual(res.relationship_count(),0)

    def test_interaction_directed_monpartite(self):
        ids = model.identifiers
        interaction = ids.objects.interaction
        pe = ids.objects.physical_entity
        gn = "test1"
        try:
            self.dg.driver.project.drop(gn)
        except ValueError:
            pass

        res = self.dg.project.interaction(gn,direction="DIRECTED",type="monopartite")
        self.assertEqual(gn,res.name())
        int_der = [str(n[1]["key"]) for n in model.get_derived(interaction)]
        pe_der = [str(n[1]["key"]) for n in model.get_derived(pe)]
        ge = res._graph_info()
        relationship_projection = ge["configuration"]["relationshipProjection"]
        for k,v in relationship_projection.items():
            if "Input" in model.get_interaction_direction(model.get_class_code(k))[0][1]["key"]:
                self.assertEqual(v["orientation"],"REVERSE")
            else:
                self.assertEqual(v["orientation"],"NATURAL")
        schema = ge["schema"]
        edges = schema["relationships"].keys()
        nodes = schema["nodes"].keys()
        pe_der += [n.get_key() for n in self.dg.driver.node_query(list(nodes))]
        for e in edges:
            self.assertIn(e,int_der)
        for n in nodes:
            self.assertIn(n,pe_der)
        self.dg.driver.project.drop(gn)

    def test_interaction_undirected_monpartite(self):
        ids = model.identifiers
        interaction = ids.objects.interaction
        pe = ids.objects.physical_entity
        gn = "test1"
        try:
            self.dg.driver.project.drop(gn)
        except ValueError:
            pass

        res = self.dg.project.interaction(gn,direction="UNDIRECTED",type="monopartite")
        self.assertEqual(gn,res.name())
        int_der = [str(n[1]["key"]) for n in model.get_derived(interaction)]
        pe_der = [str(n[1]["key"]) for n in model.get_derived(pe)]
        ge = res._graph_info()
        relationship_projection = ge["configuration"]["relationshipProjection"]
        for k,v in relationship_projection.items():
            self.assertEqual(v["orientation"],"UNDIRECTED")

        schema = ge["schema"]
        edges = schema["relationships"].keys()
        nodes = schema["nodes"].keys()
        pe_der += [n.get_key() for n in self.dg.driver.node_query(list(nodes))]
        for e in edges:
            self.assertIn(e,int_der)
        for n in nodes:            
            self.assertIn(n,pe_der)
        self.dg.driver.project.drop(gn)

    # PPi
    def test_interaction_ppi_directed_bipartite(self):
        ids = model.identifiers
        interaction = ids.objects.interaction
        pe = ids.objects.protein
        gn = "test1"
        pe_der = [str(pe)]+[str(n[1]["key"]) for n in model.get_derived(pe)] + [str(n[1]["key"]) for n in model.get_derived(interaction)]
        try:
            self.dg.driver.project.drop(gn)
        except ValueError:
            pass

        res = self.dg.project.interaction_ppi(gn,direction="DIRECTED",type="bipartite")
        self.assertEqual(gn,res.name())
        gi = res._graph_info()
        schema = gi["schema"]
        nodes = schema["nodes"].keys()
        edges = schema["relationships"].keys()
        for n in nodes:
            nt = self.dg.driver.node_query(n)[0].get_type()
            self.assertIn(nt,pe_der)
        self.dg.driver.project.drop(gn)

    def test_interaction_ppi_undirected_bipartite(self):
        ids = model.identifiers
        interaction = ids.objects.interaction
        pe = ids.objects.protein
        gn = "test1"
        int_der = [str(n[1]["key"]) for n in model.get_derived(interaction)]
        pe_der = [str(pe)]+[str(n[1]["key"]) for n in model.get_derived(pe)]
        try:
            self.dg.driver.project.drop(gn)
        except ValueError:
            pass

        res = self.dg.project.interaction_ppi(gn,direction="UNDIRECTED",type="bipartite")
        self.assertEqual(gn,res.name())
        gi = res._graph_info()
        schema = gi["schema"]
        nodes = schema["nodes"].keys()
        pe_der += [n.get_key() for n in self.dg.driver.node_query(list(nodes))]
        for n in nodes:
            self.assertIn(n,pe_der)
        self.dg.driver.project.drop(gn)

    def test_interaction_ppi_directed_monpartite(self):
        ids = model.identifiers
        interaction = ids.objects.interaction
        pe = ids.objects.protein
        gn = "test1"
        int_der = [str(n[1]["key"]) for n in model.get_derived(interaction)]
        pe_der = [str(pe)]+[str(n[1]["key"]) for n in model.get_derived(pe)]
        try:
            self.dg.driver.project.drop(gn)
        except ValueError:
            pass
        res = self.dg.project.interaction_ppi(gn,direction="DIRECTED",type="monopartite")
        self.assertEqual(gn,res.name())
        gi = res._graph_info()
        schema = gi["schema"]
        nodes = schema["nodes"].keys()
        pe_der += [n.get_key() for n in self.dg.driver.node_query(list(nodes))]
        for n in nodes:
            self.assertIn(n,pe_der)
        self.dg.driver.project.drop(gn)

    def test_interaction_ppi_undirected_monpartite(self):
        ids = model.identifiers
        interaction = ids.objects.interaction
        pe = ids.objects.protein
        gn = "test1"
        int_der = [str(n[1]["key"]) for n in model.get_derived(interaction)]
        pe_der = [str(pe)]+[str(n[1]["key"]) for n in model.get_derived(pe)]
        try:
            self.dg.driver.project.drop(gn)
        except ValueError:
            pass
        res = self.dg.project.interaction_ppi(gn,direction="UNDIRECTED",type="monopartite")
        self.assertEqual(gn,res.name())
        ge = res._graph_info()
        relationship_projection = ge["configuration"]["relationshipProjection"]
        for k,v in relationship_projection.items():
            self.assertEqual(v["orientation"],"UNDIRECTED")
        schema = ge["schema"]
        nodes = schema["nodes"].keys()
        pe_der += [n.get_key() for n in self.dg.driver.node_query(list(nodes))]
        for n in nodes:         
            self.assertIn(n,pe_der)
        self.dg.driver.project.drop(gn)

    # Genetic
    def test_interaction_genetic_directed_bipartite(self):
        ids = model.identifiers
        interaction = ids.objects.interaction
        pe = ids.objects.dna
        gn = "test1"
        int_der = [str(n[1]["key"]) for n in model.get_derived(interaction)]
        pe_der = [str(pe)]+[str(n[1]["key"]) for n in model.get_derived(pe)]
        try:
            self.dg.driver.project.drop(gn)
        except ValueError:
            pass
        res = self.dg.project.interaction_genetic(gn,direction="DIRECTED",type="bipartite")
        self.assertEqual(gn,res.name())
        gi = res._graph_info()
        schema = gi["schema"]
        nodes = schema["nodes"].keys()
        pe_der += [n.get_key() for n in self.dg.driver.node_query(list(nodes))]
        for n in nodes:
            self.assertIn(n,pe_der)

    def test_interaction_genetic_undirected_bipartite(self):
        ids = model.identifiers
        interaction = ids.objects.interaction
        pe = ids.objects.dna
        gn = "test1"
        int_der = [str(n[1]["key"]) for n in model.get_derived(interaction)]
        pe_der = [str(pe)]+[str(n[1]["key"]) for n in model.get_derived(pe)]
        try:
            self.dg.driver.project.drop(gn)
        except ValueError:
            pass
        res = self.dg.project.interaction_genetic(gn,direction="UNDIRECTED",type="bipartite")
        self.assertEqual(gn,res.name())
        gi = res._graph_info()
        schema = gi["schema"]
        nodes = schema["nodes"].keys()
        pe_der += [n.get_key() for n in self.dg.driver.node_query(list(nodes))]
        for n in nodes:
            self.assertIn(n,pe_der)
        self.dg.driver.project.drop(gn)

    def test_interaction_genetic_directed_monpartite(self):
        ids = model.identifiers
        interaction = ids.objects.interaction
        pe = ids.objects.dna
        gn = "test1"
        int_der = [str(n[1]["key"]) for n in model.get_derived(interaction)]
        pe_der = [str(pe)]+[str(n[1]["key"]) for n in model.get_derived(pe)]
        try:
            self.dg.driver.project.drop(gn)
        except ValueError:
            pass
        res = self.dg.project.interaction_genetic(gn,direction="DIRECTED",type="monopartite")
        self.assertEqual(gn,res.name())
        gi = res._graph_info()
        schema = gi["schema"]
        nodes = schema["nodes"].keys()
        pe_der += [n.get_key() for n in self.dg.driver.node_query(list(nodes))]
        for n in nodes:         
            self.assertIn(n,pe_der)
        self.dg.driver.project.drop(gn)

    def test_interaction_genetic_undirected_monpartite(self):
        ids = model.identifiers
        interaction = ids.objects.interaction
        pe = ids.objects.dna
        gn = "test1"
        int_der = [str(n[1]["key"]) for n in model.get_derived(interaction)]
        pe_der = [str(pe)]+[str(n[1]["key"]) for n in model.get_derived(pe)]
        try:
            self.dg.driver.project.drop(gn)
        except ValueError:
            pass

        res = self.dg.project.interaction_genetic(gn,direction="UNDIRECTED",type="monopartite")
        self.assertEqual(gn,res.name())
        ge = res._graph_info()
        relationship_projection = ge["configuration"]["relationshipProjection"]
        for k,v in relationship_projection.items():
            self.assertEqual(v["orientation"],"UNDIRECTED")
        schema = ge["schema"]
        nodes = schema["nodes"].keys()
        pe_der += [n.get_key() for n in self.dg.driver.node_query(list(nodes))]
        for n in nodes:         
            self.assertIn(n,pe_der)
        self.dg.driver.project.drop(gn)


