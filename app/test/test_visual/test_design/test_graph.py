import unittest
import os
import sys

from rdflib import RDF,OWL, URIRef
sys.path.insert(0, os.path.join(".."))
sys.path.insert(0, os.path.join("..",".."))

from converters.model_handler import convert as m_convert
from converters.design_handler import convert as i_convert
from graph.design import DesignGraph

curr_dir = os.path.dirname(os.path.realpath(__file__))
test_fn = os.path.join(curr_dir,"..","files","design","sbol","nor_gate.xml")
model_fn = os.path.join(curr_dir,"..","..","utility","nv_design.xml")

class TestDesignGraph(unittest.TestCase):

    def setUp(self):
        self.graph = i_convert(m_convert(model_fn),test_fn)

    def tearDown(self):
        for filename in os.listdir("."):
            if filename.endswith(".json"):
                os.remove(filename)

    def test_labels(self):
        for n,v,k,e in self.graph.edges(data=True,keys=True):
            edge_label = e["display_name"]
            self.assertIn(edge_label,k)

    def test_search(self):
        all_edges = self.graph.edges(data=True,keys=True)
        res = list(self.graph.search((None,None,None)))
        self.assertEqual(len(res),len(all_edges))
        for n,v,k,e in all_edges:
            n_data = self.graph.nodes[n]
            v_data = self.graph.nodes[v]
            expected_res_val = ([n,n_data],[v,v_data],k)
            self.assertIn(expected_res_val,res)

    def test_get_rdf_type(self):
        for n,v,e in self.graph.search((None,RDF.type,None)):
            n,n_data = n
            self.assertEqual(self.graph.get_rdf_type(n),v)
    
    def test_merge_nodes(self):
        pre_nodes = list(self.graph.nodes(data=True)) 
        pre_edges = list(self.graph.edges(keys=True,data=True)) 
        subject = self.graph.search((URIRef("http://shortbol.org/v2#Ara_arac/1"),None,None),True)[0][0]
        expected_nodes = [URIRef("http://shortbol.org/v2#NOR_gate_module/arac_ara_binding/1")]
        nodes = [self.graph.search((n,None,None),True)[0][0] for n in expected_nodes]
        self.graph.merge_nodes(subject,nodes)
        post_nodes = list(self.graph.nodes(data=True))

        for d,data in node_diff(pre_nodes,post_nodes):
            self.assertIn(data["key"],expected_nodes)

        post_edges = list(self.graph.edges(keys=True,data=True))
        expected_diff_keys = [URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'),
                              URIRef('http://www.nv_ontology.org/product'), 
                              URIRef('http://www.nv_ontology.org/consistsOf'),
                              URIRef('http://www.nv_ontology.org/consistsOf'),
                              URIRef('http://www.nv_ontology.org/reactant'),
                              URIRef('http://www.nv_ontology.org/reactant')]
        self.assertCountEqual(expected_diff_keys,[e[2] for e in edge_diff(pre_edges,post_edges)])

    def test_add_graph(self):
        fn1 = os.path.join(curr_dir,"..","files","design","sbol","0x3B.xml")
        fn2 = os.path.join(curr_dir,"..","files","design","sbol","0x87.xml")
        m_graph = m_convert(model_fn)
        graph = DesignGraph()
        g1 = i_convert(m_graph,fn1)
        g1_edges = [(g1.nodes[n]["key"],e,g1.nodes[v]["key"],k) for n,v,e,k in g1.edges(keys=True,data=True)]
        g2 = i_convert(m_graph,fn2)
        g2_edges = [(g2.nodes[n]["key"],e,g2.nodes[v]["key"],k) for n,v,e,k in g2.edges(keys=True,data=True)]
        graph.add_graph(g1)
        graph.add_graph(g2)

        for n,v,e,k in graph.edges(data=True,keys=True):
            n_data = graph.nodes[n]
            v_data = graph.nodes[v]
            trpl = (n_data["key"],e,v_data["key"],k)
            self.assertTrue((trpl in g1_edges) or (trpl in g2_edges),trpl)


def node_diff(list1,list2):
    diff = []
    for n,data in list1:
        for n1,data1 in list2:
            if n == n1 and data==data1:
                break
        else:
            diff.append((n,data))
    return diff

def edge_diff(list1,list2):
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
