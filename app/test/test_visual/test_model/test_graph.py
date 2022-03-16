from operator import eq
import unittest
import os
import sys

from rdflib import RDF,OWL,RDFS
from rdflib.term import BNode, URIRef
sys.path.insert(0, os.path.join(".."))
sys.path.insert(0, os.path.join("..",".."))
sys.path.insert(0, os.path.join("..","..",".."))
from converters.model_handler import convert as m_convert

curr_dir = os.path.dirname(os.path.realpath(__file__))
model_fn = os.path.join(curr_dir,"..","..","utility","nv_design.xml")

class TestModelGraph(unittest.TestCase):
    def setUp(self):
        self.mg = m_convert(model_fn)

    def tearDown(self):
        pass

    def test_labels(self):
        for n,v,k,e in self.mg.edges(data=True,keys=True):
            edge_label = e["display_name"]
            self.assertIn(edge_label,k)

    def test_get_class_code(self):
        for n,v,e in self.mg.edges(keys=True):
            n_key = self.mg.nodes[n]["key"]
            if e == RDF.type:
                actual_code = self.mg.get_class_code(n_key)
                self.assertEqual(actual_code,n)

    def test_search(self):
        all_edges = self.mg.edges(data=True,keys=True)
        res = list(self.mg.search((None,None,None)))
        self.assertEqual(len(res),len(all_edges))
        for n,v,k,e in all_edges:
            n_data = self.mg.nodes[n]
            v_data = self.mg.nodes[v]
            expected_res_val = ([n,n_data],[v,v_data],k)
            self.assertIn(expected_res_val,res)

    def test_get_rdf_type(self):
        for n,v,e in self.mg.search((None,RDF.type,None)):
            n,n_data = n
            self.assertEqual(self.mg.get_rdf_type(n),v)

    def test_get_classes(self):
        a_result = self.mg.get_classes()
        e_result = [c[0] for c in self.mg.search((None,RDF.type,OWL.Class))]
        self.assertCountEqual(e_result,a_result)

    def test_get_parent_classes(self):
        bases = self.mg.get_base_class()
        for node in self.mg.get_classes():
            parent = self.mg.get_parent_classes(node[0])
            if node in bases:
                self.assertEqual(len(parent),0)
            elif isinstance(node[1]["key"],BNode):
                self.assertEqual(len(parent),0)
            else:
                self.assertEqual(parent,[c[1] for c in self.mg.search((node[0],RDFS.subClassOf,None)) if not isinstance(c[1][1]["key"],BNode)])

    def test_get_child_classes(self):
        all_classes = self.mg.get_classes(False)
        scs = [c[1] for c in self.mg.search((None,RDFS.subClassOf,None))]
        leaf_classes = [c for c in all_classes if c not in scs]

        for node in self.mg.get_classes():
            children = self.mg.get_child_classes(node[0])
            if node in leaf_classes:
                self.assertEqual(len(children),0)
            elif isinstance(node[1]["key"],BNode):
                self.assertEqual(len(children),0)
            else:
                self.assertEqual(children,[c[0] for c in self.mg.search((None,RDFS.subClassOf,node[0]))])

    def test_get_class_depth(self):        
        for node,base in self.mg.get_base_class():
            expected_depth = 0
            self.assertEqual(self.mg.get_class_depth(node),expected_depth)
            children = self.mg.get_child_classes(node)
            while children != []:
                expected_depth += 1
                next_level = []
                for child,c_data in children:
                    self.assertEqual(self.mg.get_class_depth(child),expected_depth,c_data)
                    next_level += self.mg.get_child_classes(child)
                children = next_level

    def test_get_base_class(self):
        a_result = self.mg.get_base_class()
        e_result = URIRef("http://www.nv_ontology.org/Entity")
        self.assertEqual(e_result,a_result[0][1]["key"])

    def test_get_restrictions(self):
        i_t = URIRef("http://www.nv_ontology.org/Repression")
        cc = self.mg.get_class_code(i_t)
        restrictions = self.mg.get_restrictions_on(cc)
        self.assertTrue(len(restrictions) > 0)
        for restriction in restrictions:
            self.assertEqual(self.mg.get_rdf_type(restriction)[1]["key"],OWL.Restriction)


    def test_get_constraint(self):
        i_t = URIRef("http://www.nv_ontology.org/Repression")
        cc = self.mg.get_class_code(i_t)
        restrictions = {}
        for restriction in self.mg.get_restrictions_on(cc):
            predicate,constraints = self.mg.get_constraint(restriction)
            restrictions[predicate] = constraints
        self.assertTrue(len(restrictions) > 0)
        ce_code = self.mg.get_class_code(self.mg.identifiers.objects.conceptual_entity)
        for k,v in restrictions.items():
            self.assertEqual(k,self.mg.identifiers.predicates.consistsOf)
            for pred,constraint in v:
                self.assertTrue(self.mg.is_base(ce_code,constraint[0]))


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
