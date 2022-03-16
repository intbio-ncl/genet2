import unittest
import os
import sys

from rdflib import URIRef

sys.path.insert(0, os.path.join(".."))
sys.path.insert(0, os.path.join("..",".."))

from builder.protocol import ProtocolBuilder

curr_dir = os.path.dirname(os.path.realpath(__file__))
ot2_file = os.path.join(curr_dir,"..","files","opentrons","1_clip.ot2.py")
auto_file = os.path.join(curr_dir,"..","files","protocols","autoprotocol","nor_full.json")
model_file = os.path.join(curr_dir,"..","..","utility","nv_protocol.xml")

class TestSearch(unittest.TestCase):
    def setUp(self):
        self.builder = ProtocolBuilder(model_file,auto_file)
        self.graph = self.builder._graph

    def tearDown(self):
        pass

    def test_get_parent(self):
        code = self.builder.get_object_code(URIRef('http://www.nv_ontology.org/master/assembly/restriction/restriction'))
        parent = self.builder.get_parent(code)
        expected_parent = URIRef("http://www.nv_ontology.org/master/assembly/restriction")
        self.assertEqual(parent[1]["key"],expected_parent)

    def test_get_io(self):
        nv_well = self.builder._model_graph.identifiers.objects.well
        code = self.builder.get_object_code(URIRef('http://www.nv_ontology.org/master/assembly'))
        inputs,outputs = self.builder.get_io(code)
        for i_id,i_data in inputs:
            r_type = self.builder.get_rdf_type(i_id)
            self.assertEqual(r_type[1]["key"],nv_well)
        for o_id,o_data  in outputs:
            r_type = self.builder.get_rdf_type(o_id)
            self.assertEqual(r_type[1]["key"],nv_well)

    def test_get_parent(self):
        code = self.builder.get_object_code(URIRef('http://www.nv_ontology.org/master/assembly/restriction/restriction'))
        parent = self.builder.get_parent(code)
        expected_parent = URIRef("http://www.nv_ontology.org/master/assembly/restriction")
        self.assertEqual(parent[1]["key"],expected_parent)

    def test_get_abstraction_level_complex(self):
        nor_protocol = os.path.join(curr_dir,"..","files","protocols","autoprotocol","nor_full.protocol.nv")
        builder = ProtocolBuilder(model_file,nor_protocol)

        result = builder.get_abstraction_level(1)
        expected_results = [URIRef("http://www.nv_ontology.org/master/assembly"),
                            URIRef("http://www.nv_ontology.org/master/transformation"),
                            URIRef("http://www.nv_ontology.org/master/validation")]
        self.assertEqual([k[1]["key"] for k in result],expected_results)

        result = builder.get_abstraction_level(2)
        expected_results = [URIRef("http://www.nv_ontology.org/master/assembly/restriction"),
                           URIRef("http://www.nv_ontology.org/master/assembly/purification"),
                           URIRef("http://www.nv_ontology.org/master/assembly/ligation"),
                           URIRef("http://www.nv_ontology.org/master/transformation/preparecells"),
                           URIRef("http://www.nv_ontology.org/master/transformation/heatshock"),
                           URIRef("http://www.nv_ontology.org/master/transformation/outgrowth"),
                           URIRef("http://www.nv_ontology.org/master/validation/colonypcr"),
                           URIRef("http://www.nv_ontology.org/master/validation/sequencing")]
        self.assertEqual([k[1]["key"] for k in result],expected_results)

        result = builder.get_abstraction_level(3)
        expected_results = [URIRef("http://www.nv_ontology.org/master/assembly/restriction/restriction"),
                            URIRef("http://www.nv_ontology.org/master/assembly/restriction/restriction/0"),
                            URIRef("http://www.nv_ontology.org/master/assembly/purification/purify"),
                            URIRef("http://www.nv_ontology.org/master/assembly/purification/purify/0"),
                            URIRef("http://www.nv_ontology.org/master/assembly/ligation/dispense"),
                            URIRef("http://www.nv_ontology.org/master/assembly/ligation/dispense/0"),
                            URIRef("http://www.nv_ontology.org/master/assembly/ligation/dispense/1"),
                            URIRef("http://www.nv_ontology.org/master/assembly/ligation/dispense/2"),
                            URIRef("http://www.nv_ontology.org/master/assembly/ligation/seal"),
                            URIRef("http://www.nv_ontology.org/master/assembly/ligation/incubate"),
                            URIRef("http://www.nv_ontology.org/master/assembly/ligation/thermocycle"),
                            URIRef("http://www.nv_ontology.org/master/transformation/preparecells/unseal"),
                            URIRef("http://www.nv_ontology.org/master/transformation/preparecells/dispense"),
                            URIRef("http://www.nv_ontology.org/master/transformation/preparecells/dispense/0"),
                            URIRef("http://www.nv_ontology.org/master/transformation/preparecells/seal"),
                            URIRef("http://www.nv_ontology.org/master/transformation/preparecells/spin"),
                            URIRef("http://www.nv_ontology.org/master/transformation/heatshock/thermocycle"),
                            URIRef("http://www.nv_ontology.org/master/transformation/heatshock/thermocycle/0"),
                            URIRef("http://www.nv_ontology.org/master/transformation/heatshock/thermocycle/1"),
                            URIRef("http://www.nv_ontology.org/master/transformation/outgrowth/unseal"),
                            URIRef("http://www.nv_ontology.org/master/transformation/outgrowth/dispense"),
                            URIRef("http://www.nv_ontology.org/master/transformation/outgrowth/dispense/0"),
                            URIRef("http://www.nv_ontology.org/master/transformation/outgrowth/incubate"),
                            URIRef("http://www.nv_ontology.org/master/validation/colonypcr/autopick"),
                            URIRef("http://www.nv_ontology.org/master/validation/colonypcr/dispense"),
                            URIRef("http://www.nv_ontology.org/master/validation/colonypcr/dispense/0"),
                            URIRef("http://www.nv_ontology.org/master/validation/colonypcr/dispense/1"),
                            URIRef("http://www.nv_ontology.org/master/validation/colonypcr/dispense/2"),
                            URIRef("http://www.nv_ontology.org/master/validation/colonypcr/seal"),
                            URIRef("http://www.nv_ontology.org/master/validation/colonypcr/thermocycle"),
                            URIRef("http://www.nv_ontology.org/master/validation/colonypcr/thermocycle/0"),
                            URIRef("http://www.nv_ontology.org/master/validation/colonypcr/thermocycle/1"),
                            URIRef("http://www.nv_ontology.org/master/validation/colonypcr/thermocycle/2"),
                            URIRef("http://www.nv_ontology.org/master/validation/colonypcr/unseal"),
                            URIRef("http://www.nv_ontology.org/master/validation/colonypcr/gel_separate"),
                            URIRef("http://www.nv_ontology.org/master/validation/sequencing")]
        self.assertEqual([k[1]["key"] for k in result],expected_results)

        result = builder.get_abstraction_level(4)
        expected_results = [URIRef("http://www.nv_ontology.org/master/assembly/restriction/restriction/dispense"),
                            URIRef("http://www.nv_ontology.org/master/assembly/restriction/restriction/dispense/0"),
                            URIRef("http://www.nv_ontology.org/master/assembly/restriction/restriction/dispense/1"),
                            URIRef("http://www.nv_ontology.org/master/assembly/restriction/restriction/dispense/2"),
                            URIRef("http://www.nv_ontology.org/master/assembly/restriction/restriction/dispense/3"),
                            URIRef("http://www.nv_ontology.org/master/assembly/restriction/restriction/seal"),
                            URIRef("http://www.nv_ontology.org/master/assembly/restriction/restriction/spin"),
                            URIRef("http://www.nv_ontology.org/master/assembly/restriction/restriction/incubate"),
                            URIRef("http://www.nv_ontology.org/master/assembly/restriction/restriction/thermocycle"),
                            URIRef("http://www.nv_ontology.org/master/assembly/restriction/restriction/0/dispense"),
                            URIRef("http://www.nv_ontology.org/master/assembly/restriction/restriction/0/dispense/0"),
                            URIRef("http://www.nv_ontology.org/master/assembly/restriction/restriction/0/dispense/1"),
                            URIRef("http://www.nv_ontology.org/master/assembly/restriction/restriction/0/dispense/2"),
                            URIRef("http://www.nv_ontology.org/master/assembly/restriction/restriction/0/dispense/3"),
                            URIRef("http://www.nv_ontology.org/master/assembly/restriction/restriction/0/seal"),
                            URIRef("http://www.nv_ontology.org/master/assembly/restriction/restriction/0/spin"),
                            URIRef("http://www.nv_ontology.org/master/assembly/restriction/restriction/0/incubate"),
                            URIRef("http://www.nv_ontology.org/master/assembly/restriction/restriction/0/thermocycle"),
                            URIRef("http://www.nv_ontology.org/master/assembly/purification/purify/bind"),
                            URIRef("http://www.nv_ontology.org/master/assembly/purification/purify/wash"),
                            URIRef("http://www.nv_ontology.org/master/assembly/purification/purify/elution"),
                            URIRef("http://www.nv_ontology.org/master/assembly/purification/purify/0/bind"),
                            URIRef("http://www.nv_ontology.org/master/assembly/purification/purify/0/wash"),
                            URIRef("http://www.nv_ontology.org/master/assembly/purification/purify/0/elution"),
                            URIRef("http://www.nv_ontology.org/master/assembly/ligation/dispense"),
                            URIRef("http://www.nv_ontology.org/master/assembly/ligation/dispense/0"),
                            URIRef("http://www.nv_ontology.org/master/assembly/ligation/dispense/1"),
                            URIRef("http://www.nv_ontology.org/master/assembly/ligation/dispense/2"),
                            URIRef("http://www.nv_ontology.org/master/assembly/ligation/seal"),
                            URIRef("http://www.nv_ontology.org/master/assembly/ligation/incubate"),
                            URIRef("http://www.nv_ontology.org/master/assembly/ligation/thermocycle"),
                            URIRef("http://www.nv_ontology.org/master/transformation/preparecells/unseal"),
                            URIRef("http://www.nv_ontology.org/master/transformation/preparecells/dispense"),
                            URIRef("http://www.nv_ontology.org/master/transformation/preparecells/dispense/0"),
                            URIRef("http://www.nv_ontology.org/master/transformation/preparecells/seal"),
                            URIRef("http://www.nv_ontology.org/master/transformation/preparecells/spin"),
                            URIRef("http://www.nv_ontology.org/master/transformation/heatshock/thermocycle"),
                            URIRef("http://www.nv_ontology.org/master/transformation/heatshock/thermocycle/0"),
                            URIRef("http://www.nv_ontology.org/master/transformation/heatshock/thermocycle/1"),
                            URIRef("http://www.nv_ontology.org/master/transformation/outgrowth/unseal"),
                            URIRef("http://www.nv_ontology.org/master/transformation/outgrowth/dispense"),
                            URIRef("http://www.nv_ontology.org/master/transformation/outgrowth/dispense/0"),
                            URIRef("http://www.nv_ontology.org/master/transformation/outgrowth/incubate"),
                            URIRef("http://www.nv_ontology.org/master/validation/colonypcr/autopick"),
                            URIRef("http://www.nv_ontology.org/master/validation/colonypcr/dispense"),
                            URIRef("http://www.nv_ontology.org/master/validation/colonypcr/dispense/0"),
                            URIRef("http://www.nv_ontology.org/master/validation/colonypcr/dispense/1"),
                            URIRef("http://www.nv_ontology.org/master/validation/colonypcr/dispense/2"),
                            URIRef("http://www.nv_ontology.org/master/validation/colonypcr/seal"),
                            URIRef("http://www.nv_ontology.org/master/validation/colonypcr/thermocycle"),
                            URIRef("http://www.nv_ontology.org/master/validation/colonypcr/thermocycle/0"),
                            URIRef("http://www.nv_ontology.org/master/validation/colonypcr/thermocycle/1"),
                            URIRef("http://www.nv_ontology.org/master/validation/colonypcr/thermocycle/2"),
                            URIRef("http://www.nv_ontology.org/master/validation/colonypcr/unseal"),
                            URIRef("http://www.nv_ontology.org/master/validation/colonypcr/gel_separate"),
                            URIRef("http://www.nv_ontology.org/master/validation/sequencing")]
        self.assertEqual([k[1]["key"] for k in result],expected_results) 

        result = builder.get_abstraction_level(5)
        expected_results = [ URIRef("http://www.nv_ontology.org/master/assembly/restriction/restriction/dispense"),
                             URIRef("http://www.nv_ontology.org/master/assembly/restriction/restriction/dispense/0"),
                             URIRef("http://www.nv_ontology.org/master/assembly/restriction/restriction/dispense/1"),
                             URIRef("http://www.nv_ontology.org/master/assembly/restriction/restriction/dispense/2"),
                             URIRef("http://www.nv_ontology.org/master/assembly/restriction/restriction/dispense/3"),
                             URIRef("http://www.nv_ontology.org/master/assembly/restriction/restriction/seal"),
                             URIRef("http://www.nv_ontology.org/master/assembly/restriction/restriction/spin"),
                             URIRef("http://www.nv_ontology.org/master/assembly/restriction/restriction/incubate"),
                             URIRef("http://www.nv_ontology.org/master/assembly/restriction/restriction/thermocycle"),
                             URIRef("http://www.nv_ontology.org/master/assembly/restriction/restriction/0/dispense"),
                             URIRef("http://www.nv_ontology.org/master/assembly/restriction/restriction/0/dispense/0"),
                             URIRef("http://www.nv_ontology.org/master/assembly/restriction/restriction/0/dispense/1"),
                             URIRef("http://www.nv_ontology.org/master/assembly/restriction/restriction/0/dispense/2"),
                             URIRef("http://www.nv_ontology.org/master/assembly/restriction/restriction/0/dispense/3"),
                             URIRef("http://www.nv_ontology.org/master/assembly/restriction/restriction/0/seal"),
                             URIRef("http://www.nv_ontology.org/master/assembly/restriction/restriction/0/spin"),
                             URIRef("http://www.nv_ontology.org/master/assembly/restriction/restriction/0/incubate"),
                             URIRef("http://www.nv_ontology.org/master/assembly/restriction/restriction/0/thermocycle"),
                             URIRef("http://www.nv_ontology.org/master/assembly/purification/purify/bind/unseal"),
                             URIRef("http://www.nv_ontology.org/master/assembly/purification/purify/bind/dispense"),
                             URIRef("http://www.nv_ontology.org/master/assembly/purification/purify/bind/seal"),
                             URIRef("http://www.nv_ontology.org/master/assembly/purification/purify/bind/spin"),
                             URIRef("http://www.nv_ontology.org/master/assembly/purification/purify/wash/unseal"),
                             URIRef("http://www.nv_ontology.org/master/assembly/purification/purify/wash/dispense"),
                             URIRef("http://www.nv_ontology.org/master/assembly/purification/purify/wash/seal"),
                             URIRef("http://www.nv_ontology.org/master/assembly/purification/purify/wash/spin"),
                             URIRef("http://www.nv_ontology.org/master/assembly/purification/purify/elution/unseal"),
                             URIRef("http://www.nv_ontology.org/master/assembly/purification/purify/elution/dispense"),
                             URIRef("http://www.nv_ontology.org/master/assembly/purification/purify/elution/seal"),
                             URIRef("http://www.nv_ontology.org/master/assembly/purification/purify/elution/incubate"),
                             URIRef("http://www.nv_ontology.org/master/assembly/purification/purify/elution/spin"),
                             URIRef("http://www.nv_ontology.org/master/assembly/purification/purify/elution/unseal/0"),
                             URIRef("http://www.nv_ontology.org/master/assembly/purification/purify/elution/dispense/0"),
                             URIRef("http://www.nv_ontology.org/master/assembly/purification/purify/0/bind/unseal"),
                             URIRef("http://www.nv_ontology.org/master/assembly/purification/purify/0/bind/dispense"),
                             URIRef("http://www.nv_ontology.org/master/assembly/purification/purify/0/bind/seal"),
                             URIRef("http://www.nv_ontology.org/master/assembly/purification/purify/0/bind/spin"),
                             URIRef("http://www.nv_ontology.org/master/assembly/purification/purify/0/wash/unseal"),
                             URIRef("http://www.nv_ontology.org/master/assembly/purification/purify/0/wash/dispense"),
                             URIRef("http://www.nv_ontology.org/master/assembly/purification/purify/0/wash/seal"),
                             URIRef("http://www.nv_ontology.org/master/assembly/purification/purify/0/wash/spin"),
                             URIRef("http://www.nv_ontology.org/master/assembly/purification/purify/0/elution/unseal"),
                             URIRef("http://www.nv_ontology.org/master/assembly/purification/purify/0/elution/dispense"),
                             URIRef("http://www.nv_ontology.org/master/assembly/purification/purify/0/elution/seal"),
                             URIRef("http://www.nv_ontology.org/master/assembly/purification/purify/0/elution/incubate"),
                             URIRef("http://www.nv_ontology.org/master/assembly/purification/purify/0/elution/spin"),
                             URIRef("http://www.nv_ontology.org/master/assembly/purification/purify/0/elution/unseal/0"),
                             URIRef("http://www.nv_ontology.org/master/assembly/purification/purify/0/elution/dispense/0"),
                             URIRef("http://www.nv_ontology.org/master/assembly/ligation/dispense"),
                             URIRef("http://www.nv_ontology.org/master/assembly/ligation/dispense/0"),
                             URIRef("http://www.nv_ontology.org/master/assembly/ligation/dispense/1"),
                             URIRef("http://www.nv_ontology.org/master/assembly/ligation/dispense/2"),
                             URIRef("http://www.nv_ontology.org/master/assembly/ligation/seal"),
                             URIRef("http://www.nv_ontology.org/master/assembly/ligation/incubate"),
                             URIRef("http://www.nv_ontology.org/master/assembly/ligation/thermocycle"),
                             URIRef("http://www.nv_ontology.org/master/transformation/preparecells/unseal"),
                             URIRef("http://www.nv_ontology.org/master/transformation/preparecells/dispense"),
                             URIRef("http://www.nv_ontology.org/master/transformation/preparecells/dispense/0"),
                             URIRef("http://www.nv_ontology.org/master/transformation/preparecells/seal"),
                             URIRef("http://www.nv_ontology.org/master/transformation/preparecells/spin"),
                             URIRef("http://www.nv_ontology.org/master/transformation/heatshock/thermocycle"),
                             URIRef("http://www.nv_ontology.org/master/transformation/heatshock/thermocycle/0"),
                             URIRef("http://www.nv_ontology.org/master/transformation/heatshock/thermocycle/1"),
                             URIRef("http://www.nv_ontology.org/master/transformation/outgrowth/unseal"),
                             URIRef("http://www.nv_ontology.org/master/transformation/outgrowth/dispense"),
                             URIRef("http://www.nv_ontology.org/master/transformation/outgrowth/dispense/0"),
                             URIRef("http://www.nv_ontology.org/master/transformation/outgrowth/incubate"),
                             URIRef("http://www.nv_ontology.org/master/validation/colonypcr/autopick"),
                             URIRef("http://www.nv_ontology.org/master/validation/colonypcr/dispense"),
                             URIRef("http://www.nv_ontology.org/master/validation/colonypcr/dispense/0"),
                             URIRef("http://www.nv_ontology.org/master/validation/colonypcr/dispense/1"),
                             URIRef("http://www.nv_ontology.org/master/validation/colonypcr/dispense/2"),
                             URIRef("http://www.nv_ontology.org/master/validation/colonypcr/seal"),
                             URIRef("http://www.nv_ontology.org/master/validation/colonypcr/thermocycle"),
                             URIRef("http://www.nv_ontology.org/master/validation/colonypcr/thermocycle/0"),
                             URIRef("http://www.nv_ontology.org/master/validation/colonypcr/thermocycle/1"),
                             URIRef("http://www.nv_ontology.org/master/validation/colonypcr/thermocycle/2"),
                             URIRef("http://www.nv_ontology.org/master/validation/colonypcr/unseal"),
                             URIRef("http://www.nv_ontology.org/master/validation/colonypcr/gel_separate"),
                             URIRef("http://www.nv_ontology.org/master/validation/sequencing")]
        self.assertEqual([k[1]["key"] for k in result],expected_results) 
        

class TestViews(unittest.TestCase):
    def setUp(self):
        self.builder = ProtocolBuilder(model_file,auto_file)
        self.model = self.builder._model_graph
        
    def tearDown(self):
        pass

    def test_pruned(self):
        self.builder.set_pruned_view()
        graph = self.builder.view

    def test_hierarchy(self):
        self.builder.set_hierarchy_view()
        graph = self.builder.view

    def test_instructions(self):
        self.builder.set_instructions_view(2,True)
        graph = self.builder.view

    def test_flow(self):
        self.builder.set_flow_view(2,False)
        graph = self.builder.view

    def test_io(self):
        self.builder.set_io_view(1,False)
        graph = self.builder.view

    def test_container(self):
        self.builder.set_container_view(False)
        graph = self.builder.view

    def test_process(self):
        self.builder.set_process_view(2,False)
        graph = self.builder.view

class TestModes(unittest.TestCase):
        def setUp(self):
            self.builder = ProtocolBuilder(model_file,auto_file)

        def tearDown(self):
            pass
        
def _graph_element_check(graph):
    node_id_map = {}
    for n,v,e in graph.edges(keys=True):
        n_data = graph.nodes[n]
        v_data = graph.nodes[v]
        if n in node_id_map.keys():
            if node_id_map[n] != n_data["key"]:
                return False
        else:
            node_id_map[n] = n_data["key"]
        if v in node_id_map.keys():
            if node_id_map[v] != v_data["key"]:
                return False
        else:
            node_id_map[v] = v_data["key"]
    return True

def _diff(list1,list2):
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
