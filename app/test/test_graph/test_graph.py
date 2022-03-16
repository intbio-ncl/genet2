import sys
import os
sys.path.insert(0, os.path.join(".."))
sys.path.insert(0, os.path.join("..",".."))
sys.path.insert(0, os.path.join("..","..",".."))
import unittest
from app.graph.nv_graph import NVGraph
from app.graph.converter.design.utility.graph import SBOLGraph
curr_dir = os.path.dirname(os.path.realpath(__file__))

test_fn = os.path.join(curr_dir,"..","files","output.xml")
class TestGraph(unittest.TestCase):
    def setUp(self):
        self._wrapper = NVGraph()
        self._rdf = SBOLGraph(test_fn)
        self._backup = self._wrapper.get_all_edges()
        self._wrapper.purge()
        self._wrapper.add_graph(test_fn)

    def tearDown(self):
        self._wrapper.purge()
        if len(self._backup) > 0:
            for edge in self._backup:
                n = self._wrapper.add_node(edge.n)
                v = self._wrapper.add_node(edge.v)
                self._wrapper.add_edge(n,v,edge)
            self._wrapper.submit()

    def test_add_graph(self):
        type_role_map = {
            "http://www.nv_ontology.org/Complex" : "http://www.biopax.org/release/biopax-level3.owl#Complex",
            "http://www.nv_ontology.org/DNA"     : ["http://www.biopax.org/release/biopax-level3.owl#Dna","http://www.biopax.org/release/biopax-level3.owl#DnaRegion","http://identifiers.org/so/SO:0000804"],
            "http://www.nv_ontology.org/SmallMolecule" : "http://www.biopax.org/release/biopax-level3.owl#SmallMolecule",
            "http://www.nv_ontology.org/Protein":"http://www.biopax.org/release/biopax-level3.owl#Protein",
            "http://www.nv_ontology.org/Promoter" : "http://identifiers.org/so/SO:0000167",
            "http://www.nv_ontology.org/RBS" : "http://identifiers.org/so/SO:0000139",
            "http://www.nv_ontology.org/Terminator" : "http://identifiers.org/so/SO:0000141" ,
            "http://www.nv_ontology.org/CDS" : "http://identifiers.org/so/SO:0000316",
            "http://www.nv_ontology.org/Repression":"http://identifiers.org/biomodels.sbo/SBO:0000169",
            "http://www.nv_ontology.org/Degradation":"http://identifiers.org/biomodels.sbo/SBO:0000179",
            "http://www.nv_ontology.org/Activation": "http://identifiers.org/biomodels.sbo/SBO:0000170",
            "http://www.nv_ontology.org/GeneticProduction":"http://identifiers.org/biomodels.sbo/SBO:0000589",
            "http://www.nv_ontology.org/Binds" : "http://identifiers.org/biomodels.sbo/SBO:0000177"
        }
        pe = self._wrapper.get_physical_entities()
        cds = self._rdf.get_component_definitions()
        self.assertEqual(len(pe),len(cds))
        for p in pe:
            p_n_lab = p.n.get_labels()[0]
            p_v_lab = p.v.get_labels()[0]
            for c in cds:
                if p_n_lab == str(c):
                    types = self._rdf.get_type(c)
                    roles = self._rdf.get_roles(c)
                    if roles != []:
                        assert(len(roles) == 1)
                        self.assertIn(str(roles[0]),type_role_map[p_v_lab])
                    else:
                        self.assertIn(str(types),type_role_map[p_v_lab])

                    p_children = self._wrapper.get_children(p.n)
                    s_children = [str(self._rdf.get_definition(n)) for n in self._rdf.get_components(c)]
                    self.assertEqual(len(pe),len(cds))
                    for p_child in p_children:
                        self.assertIn(p_child.v.get_labels()[0],s_children)
                    break
            else:
                self.fail(p)

        conceptual_entity_p = self._wrapper._model.identifiers.objects.conceptual_entity
        ce = self._wrapper.get_interactions()
        ints = self._rdf.get_interactions()
        cep = [conceptual_entity_p] + [str(c[1]["key"]) for c in self._wrapper._model.get_derived(conceptual_entity_p)]
        self.assertEqual(len(ce),len(ints))
        for c in ce:
            c_n_lab = c.n.get_labels()[0]
            c_v_lab = c.v.get_labels()[0]
            for i in ints:
                if c_n_lab == str(i):
                    types = self._rdf.get_type(i)
                    self.assertIn(str(types),type_role_map[c_v_lab])
                    co = self._wrapper.get_consists_of(c.n)
                    self.assertEqual(len(co),1)
                    co = co[0]
                    items = self._wrapper.derive_consistsOf(co.v)
                    for i in items:
                        item_type = self._wrapper.get_object_type(i)
                        self.assertTrue(len(set(cep) & set(item_type.get_labels())) > 0)
                    break

            else:
                self.fail(p)
        all_nodes = self._wrapper.get_all_nodes()
        self.assertCountEqual(list(set(all_nodes)),all_nodes)
        all_edges = self._wrapper.get_all_edges()
        self.assertCountEqual(list(set(all_edges)),all_edges)
    
    def test_add_graph_ignore(self):
        # Case: When the node is found within the graph nothing happens.
        pre_nodes = self._wrapper.get_all_nodes()
        pre_edges = self._wrapper.get_all_edges()
        self._wrapper.add_graph(test_fn)
        post_nodes = self._wrapper.get_all_nodes()
        post_edges = self._wrapper.get_all_edges()

        self.assertEqual(len(post_nodes),len(pre_nodes))
        self.assertEqual(len(post_edges),len(pre_edges))
        self.assertCountEqual(pre_nodes,post_nodes)
        self.assertCountEqual(pre_edges,post_edges)
        
        e = post_edges[0]
        n = e.n
        v = e.v
        n.add_property("test","test")
        v.add_property("test1","test2")
        e.add_property("test3","test4")
        self._wrapper.add_edge(n=n,v=v,e=e)

        post_nodes = self._wrapper.get_all_nodes()
        post_edges = self._wrapper.get_all_edges()

        post_node_props = [p.get_properties() for p in post_nodes]
        post_edge_props = [p.get_properties() for p in post_edges]
        pre_node_props = [p.get_properties() for p in pre_nodes]
        pre_edge_props = [p.get_properties() for p in pre_edges]

        self.assertEqual(len(post_nodes),len(pre_nodes))
        self.assertEqual(len(post_edges),len(pre_edges))
        self.assertCountEqual(pre_nodes,post_nodes)
        self.assertCountEqual(pre_edges,post_edges)
        self.assertCountEqual(post_node_props,pre_node_props)
        self.assertCountEqual(post_edge_props,pre_edge_props)
        
    def test_add_graph_merge(self):
        # Case: When the node is found within the graph we add any new properties.
        # Technically new labels mean new node.
        pre_nodes = self._wrapper.get_all_nodes()
        pre_edges = self._wrapper.get_all_edges()
        self._wrapper.add_graph(test_fn,mode="merge")
        post_nodes = self._wrapper.get_all_nodes()
        post_edges = self._wrapper.get_all_edges()

        self.assertEqual(len(post_nodes),len(pre_nodes))
        self.assertEqual(len(post_edges),len(pre_edges))
        self.assertCountEqual(pre_nodes,post_nodes)
        self.assertCountEqual(pre_edges,post_edges)
        
        e = post_edges[0]
        n = e.n
        v = e.v
        props = [{"key": "test","value":"test1"},{"key": "test2","value":"test3"},{"key": "test4","value":"test5"}]
        n.add_property(**props[0])
        v.add_property(**props[1])
        e.add_property(**props[2])
        self._wrapper.add_edge(n=n,v=v,e=e,mode="merge")
        self._wrapper.submit()

        post_nodes = self._wrapper.get_all_nodes()
        post_edges = self._wrapper.get_all_edges()

        p_e = self._wrapper.edge_query(n=n,e=e,v=v)
        self.assertTrue(len(p_e),1)
        p_e = p_e[0]
        p_n = p_e.n
        p_v = p_e.v
        
        p_e_props = p_e.get_properties()
        p_n_props = p_n.get_properties()
        p_v_props = p_v.get_properties()

        self.assertEqual(e.get_properties(),p_e_props)
        self.assertEqual(v.get_properties(),p_v_props)
        self.assertEqual(n.get_properties(),p_n_props)

    def test_add_graph_duplicate(self):
        pre_nodes = self._wrapper.get_all_nodes()
        pre_edges = self._wrapper.get_all_edges()
        self._wrapper.add_graph(test_fn,mode="duplicate")
        post_nodes = self._wrapper.get_all_nodes()
        post_edges = self._wrapper.get_all_edges()
        self.assertEqual(len(post_nodes),len(pre_nodes) * 2,len(post_nodes))
        self.assertEqual(len(post_edges),len(pre_edges) * 2,len(post_edges))
        self.assertCountEqual(post_nodes,pre_nodes*2)
        self.assertCountEqual(post_edges,pre_edges*2)

    def test_add_graph_overwrite(self):
        pre_nodes = self._wrapper.get_all_nodes()
        pre_edges = self._wrapper.get_all_edges()
        self._wrapper.add_graph(test_fn,mode="overwrite")
        post_nodes = self._wrapper.get_all_nodes()
        post_edges = self._wrapper.get_all_edges()

        self.assertEqual(len(post_nodes),len(pre_nodes))
        self.assertEqual(len(post_edges),len(pre_edges))
        self.assertCountEqual(pre_nodes,post_nodes)
        self.assertCountEqual(pre_edges,post_edges)
        
        e = post_edges[0]
        n = e.n
        v = e.v
        props = [{"key": "test","value":"test1"},{"key": "test2","value":"test3"},{"key": "test4","value":"test5"}]
        n.properties = {}
        v.properties = {}
        e.properties = {}
        n.add_property(**props[0])
        v.add_property(**props[1])
        e.add_property(**props[2])
        self._wrapper.add_edge(n=n,v=v,e=e,mode="overwrite")
        self._wrapper.submit()

        post_nodes = self._wrapper.get_all_nodes()
        post_edges = self._wrapper.get_all_edges()

        p_e = self._wrapper.edge_query(n=n,e=e,v=v)
        self.assertTrue(len(p_e),1)
        p_e = p_e[0]
        p_n = p_e.n
        p_v = p_e.v
        actual_props = [p_n.get_properties(),p_v.get_properties(),p_e.get_properties()]
        ex_props = [{"test":"test1"},{"test2":"test3"},{"test4":"test5"}]
        self.assertEqual(ex_props,actual_props)

    def test_add_graph_multiple_type(self):
        self._wrapper.add_graph(test_fn,mode="overwrite")
        self._wrapper.add_graph(test_fn,mode="duplicate")
        self._wrapper.add_graph(test_fn,mode="merge")