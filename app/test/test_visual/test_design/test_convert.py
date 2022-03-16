import unittest
import os
import sys
import re
import json

from rdflib import RDF
from networkx.readwrite import json_graph
from rdflib.term import URIRef

sys.path.insert(0, os.path.join(".."))
sys.path.insert(0, os.path.join("..",".."))
sys.path.insert(0, os.path.join("..","..",".."))

from converters.design_handler import convert as design_convert
from converters.model_handler import convert as model_convert
from converters.design.utility.graph import SBOLGraph
from graph.design import DesignGraph

curr_dir = os.path.dirname(os.path.realpath(__file__))
model_fn = os.path.join(curr_dir,"..","..","utility","nv_design.xml")
test_dir = os.path.join(curr_dir,"..","files","design","sbol")

class TestConvertDesign(unittest.TestCase):

    def setUp(self):
        None

    def tearDown(self):
        None

    def test_sbol_cds(self):
        filename = os.path.join(test_dir,"test_convert_sbol_cds.xml")
        model_graph = model_convert(model_fn)
        graph = design_convert(model_graph,filename)
        rdf_graph = SBOLGraph(filename)
        subjects = [t[0] for t in rdf_graph.search((None,None,None))]

        for n,v,k in graph.edges(keys=True):
            n_data = graph.nodes[n]
            v_data = graph.nodes[v]
            self.assertIn(n_data["key"],subjects)
            if k == RDF.type:
                # Purposefully named entities same as types for testing.
                e_t = _get_name(n_data["key"])
                a_t = _get_name(v_data["key"])
                self.assertEqual(a_t,e_t)

    def test_sbol_entity_entity(self):
        filename = os.path.join(test_dir,"test_convert_sbol_entity_entity.xml")
        model_graph = model_convert(model_fn)
        graph = design_convert(model_graph,filename)
        rdf_graph = SBOLGraph(filename)
        expected_edges = []

        for cd in rdf_graph.get_component_definitions():
            related_cds = [rdf_graph.get_definition(c) for c in rdf_graph.get_components(cd)]
            [expected_edges.append((cd,None,rc)) for rc in related_cds]
        
        part_of_pred = URIRef("http://www.nv_ontology.org/hasPart")
        edge_keys = [k for n,v,k in graph.edges(keys=True)]
        e_e_edges = [k for k in edge_keys if k == part_of_pred]
        self.assertEqual(len(e_e_edges),len(expected_edges))
        for n,v,k in graph.edges(keys=True):
            if k != part_of_pred:
                continue
            n_data = graph.nodes[n]
            v_data = graph.nodes[v]
            actual_edge = (n_data["key"],None,v_data["key"])
            self.assertIn(actual_edge,expected_edges)
        
    def test_sbol_interactions(self):
        filename = os.path.join(test_dir,"test_sbol_interactions.xml")
        model_graph = model_convert(model_fn)
        graph = design_convert(model_graph,filename)
        self._run_type_test(graph,model_graph)

    def test_sbol_nor_gate(self):
        filename = os.path.join(test_dir,"nor_gate.xml")
        model_graph = model_convert(model_fn)
        graph = design_convert(model_graph,filename)
        self._run_type_test(graph,model_graph)


    def test_convert_sbol(self):
        filename = os.path.join(test_dir,"multiplexer.xml")
        model_graph = model_convert(model_fn)
        graph = design_convert(model_graph,filename)
        rdf_graph = SBOLGraph(filename)
        expected_edges = []
        for cd in rdf_graph.get_component_definitions():
            related_cds = [rdf_graph.get_definition(c) for c in rdf_graph.get_components(cd)]
            [expected_edges.append((cd,None,rc)) for rc in related_cds]
        
        part_of_pred = URIRef("http://www.nv_ontology.org/hasPart")
        edge_keys = [k for n,v,k in graph.edges(keys=True)]
        e_e_edges = [k for k in edge_keys if k == part_of_pred]
        self.assertEqual(len(e_e_edges),len(expected_edges))
        self._run_type_test(graph,model_graph)
        for n,v,k in graph.edges(keys=True):
            if k != part_of_pred:
                continue
            n_data = graph.nodes[n]
            v_data = graph.nodes[v]
            actual_edge = (n_data["key"],None,v_data["key"])
            self.assertIn(actual_edge,expected_edges)

    def _run_type_test(self,graph,model):
        i_code = model.get_class_code(model.identifiers.objects.interaction)
        r_code = model.get_class_code(model.identifiers.objects.reaction)
        for n,v,e in graph.search((None,RDF.type,None)):
            v,v_data = v
            self.assertTrue(v_data["key"],model.identifiers.objects)
            if model.is_derived(v_data["key"],i_code):
                self._run_interaction_tests(n,graph,model)

    def _run_interaction_tests(self,n,graph,model):
        n,n_data = n
        consistsOf = [c[1] for c in graph.search((n,model.identifiers.predicates.consistsOf,None))]
        i_code = model.get_class_code(model.identifiers.objects.interaction)
        r_code = model.get_class_code(model.identifiers.objects.reaction)
        rdf_type = graph.get_rdf_type(n)
        model_code = model.get_class_code(rdf_type[1]["key"])

        restrictions = {}
        for restriction in model.get_restrictions_on(model_code):
            predicate,constraints = model.get_constraint(restriction)
            restrictions[predicate] = constraints
        for c in consistsOf:
            c,c_data = c
            r_key = None
            count = 0
            while r_key != RDF.nil:
                cur = [c[1] for c in graph.search((c,RDF.first,None))]
                rest = [r[1] for r in graph.search((c,RDF.rest,None))]
                self.assertEqual(len(cur),1)
                self.assertEqual(len(rest),1)
                r_key = rest[0][1]["key"]
                cur = cur[0]
                element_type = graph.get_rdf_type(cur[0])
                e_t_key = element_type[1]["key"]
                for pred,restriction in restrictions.items():
                    if e_t_key != restriction[count][1][1]["key"]:
                        raise ValueError(e_t_key,restriction[count][1][1]["key"],count)
                    
                if model.is_derived(e_t_key,r_code):
                    self._run_reaction_tests(cur[0],graph,model)
                elif model.is_derived(e_t_key,i_code):
                    self._run_interaction_tests(cur[0],graph,model)
                else:
                    self.fail("Interaction consists of something not interaction or reaction.")
                count +=1
                c = rest[0][0]
    
    def _run_reaction_tests(self,n,graph,model):
        n_type = graph.get_rdf_type(n)
        self.assertTrue(n_type[1]["key"],model.identifiers.objects)

def _get_name(subject):
    split_subject = _split(subject)
    if len(split_subject[-1]) == 1 and split_subject[-1].isdigit():
        return split_subject[-2]
    else:
        return split_subject[-1]

def _split(uri):
    return re.split('#|\/|:', uri)

def is_node(graph,subject):
    for n,data in graph.nodes(data=True):
        if subject == data["key"]:
            return True
    return False

def is_edge(graph,s,p,o):
    for n,v,k in graph.edges(keys=True):
        n_k = graph.nodes[n]["key"]
        v_k = graph.nodes[v]["key"]
        if s == n_k and p == k and o == v_k:
            return True
    return False

def diff(list1,list2):
    diff = []
    for n,v,e,k in list1:
        for n1,v1,e1,k1 in list2:
            if n == n1 and v == v1 and e == e1 and k == k1:
                break
        else:
            diff.append((n,v,e,k))
    return diff
if __name__ == '__main__':
    unittest.main()
