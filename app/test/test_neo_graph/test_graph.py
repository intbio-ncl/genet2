import sys
import os
import copy
sys.path.insert(0, os.path.join(".."))
sys.path.insert(0, os.path.join("..",".."))
sys.path.insert(0, os.path.join("..","..",".."))
import unittest
from app.graphs.neo_graph.nv_graph import NVGraph
from app.graphs.neo_graph.converter.design.utility.graph import SBOLGraph
from app.dashboards.builder.projection import ProjectionBuilder
curr_dir = os.path.dirname(os.path.realpath(__file__))

test_fn = os.path.join(curr_dir,"..","files","design","sbol","nor_full.xml")
class TestGraph(unittest.TestCase):
    def setUp(self):
        self._wrapper = NVGraph()
        self._builder = ProjectionBuilder(self._wrapper)
        self._rdf = SBOLGraph(test_fn)
        #self._backup = self._wrapper.get_all_edges()
        #self._wrapper.purge()
        #self._wrapper.add_graph(test_fn)

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
            p_n_lab = p.get_key()
            p_v_lab = p.get_type()
            for c in cds:
                if p_n_lab == str(c):
                    types = self._rdf.get_type(c)
                    roles = self._rdf.get_roles(c)
                    if roles != []:
                        assert(len(roles) == 1)
                        self.assertIn(str(roles[0]),type_role_map[p_v_lab])
                    else:
                        self.assertIn(str(types),type_role_map[p_v_lab])
                    p_children = self._wrapper.get_children(p)
                    s_children = [str(self._rdf.get_definition(n)) for n in self._rdf.get_components(c)]
                    self.assertEqual(len(pe),len(cds))
                    for p_child in p_children:
                        self.assertIn(p_child.v.get_labels()[0],s_children)
                    break
            else:
                self.fail(p)

        conceptual_entity_p = self._wrapper.model.identifiers.objects.conceptual_entity
        ce = self._wrapper.get_interactions()
        ints = self._rdf.get_interactions()
        cep = [conceptual_entity_p] + [str(c[1]["key"]) for c in self._wrapper.model.get_derived(conceptual_entity_p)]
        self.assertEqual(len(ce),len(ints))
        for c in ce:
            c_n_lab = c.get_key()
            c_v_lab = c.get_type()
            for i in ints:
                if c_n_lab == str(i):
                    types = self._rdf.get_type(i)
                    self.assertIn(str(types),type_role_map[c_v_lab])
                    co = self._wrapper.get_consists_of(c)
                    self.assertEqual(len(co),1)
                    co = co[0]
                    items = self._wrapper.derive_consistsOf(co.v)
                    for i in items:
                        self.assertTrue(i.get_type() in cep)
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
        n_props = copy.deepcopy(n.get_properties())
        v_props = copy.deepcopy(v.get_properties())
        e_props = copy.deepcopy(e.get_properties())
        
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
        self.assertEqual(e_props,p_e_props)
        self.assertEqual(v_props,p_v_props)
        self.assertEqual(n_props,p_n_props)

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

    def test_get_graph_names(self):
        self._wrapper.purge()
        self._wrapper.add_graph(test_fn)
        self.assertEqual(len(self._wrapper.get_graph_names()),1)

        self._wrapper.add_graph(test_fn,mode="duplicate")
        self.assertEqual(len(self._wrapper.get_graph_names()),2)

        self._wrapper.add_graph(test_fn,mode="overwrite")
        self.assertEqual(len(self._wrapper.get_graph_names()),2)

        self._wrapper.add_graph(test_fn,mode="merge")
        self.assertEqual(len(self._wrapper.get_graph_names()),3)

    def test_remove_graph(self):
        self._wrapper.purge()
        graph_name_1 = "Test1"
        graph_name_2 = "Test2"
        self._wrapper.add_graph(test_fn,name=graph_name_1) 
        self._wrapper.add_graph(test_fn,name=graph_name_2)
        self._wrapper.remove_graph(graph_name_1)
        self.assertEqual(self._wrapper.get_all_nodes(),[])
        self.assertEqual(self._wrapper.get_all_edges(),[])

        self._wrapper.add_graph(test_fn,name=graph_name_1) 
        pn = self._wrapper.get_all_nodes()
        pe = self._wrapper.get_all_edges()
        self._wrapper.add_graph(test_fn,name=graph_name_2,mode="duplicate")
        self._wrapper.remove_graph(graph_name_2)
        self.assertCountEqual(self._wrapper.get_all_nodes(),pn)
        self.assertCountEqual(self._wrapper.get_all_edges(),pe)
        
        self._wrapper.add_graph(test_fn,name=graph_name_1,mode="merge")
        self._wrapper.remove_graph(graph_name_2)
        self.assertCountEqual(self._wrapper.get_all_nodes(),pn)
        self.assertCountEqual(self._wrapper.get_all_edges(),pe)

class TestGDSProject(unittest.TestCase):
    def setUp(self):
        self._wrapper = NVGraph()
        self._builder = ProjectionBuilder(self._wrapper)
        self._rdf = SBOLGraph(test_fn)
        #self._backup = self._wrapper.get_all_edges()
        #self._wrapper.purge()
        #self._wrapper.add_graph(test_fn)

    def tearDown(self):
        return
        self._wrapper.purge()
        if len(self._backup) > 0:
            for edge in self._backup:
                n = self._wrapper.add_node(edge.n)
                v = self._wrapper.add_node(edge.v)
                self._wrapper.add_edge(n,v,edge)
            self._wrapper.submit()

    def test_project_interaction_bi(self):
        model = self._wrapper.model
        ids = self._wrapper.ids
        interaction = ids.objects.interaction
        pe = ids.objects.physical_entity
        gn = "test1"
        try:
            self._wrapper.project.drop(gn)
        except ValueError:
            pass

        res =   self._wrapper.project.preset(gn,"interaction_bipartite")
        self.assertEqual(gn,res.name())
        graph = self._builder.build_projection_graph(res)
        int_der = [str(n[1]["key"]) for n in model.get_derived(interaction)]
        pe_der = [str(n[1]["key"]) for n in model.get_derived(pe)]
        ip = [str(n[1]["key"]) for n in model.interaction_predicates()]
        for e in graph.edges():
            n = e.n
            v = e.v
            self.assertIn(n.get_type(),int_der)
            self.assertIn(v.get_type(),pe_der)
            self.assertIn(e.get_type(),ip)
        self._wrapper.project.drop(gn)

    def test_project_interaction_mono(self):
        model = self._wrapper.model
        ids = self._wrapper.ids
        interaction = ids.objects.interaction
        pe = ids.objects.physical_entity
        gn = "test1"
        try:
            self._wrapper.project.drop(gn)
        except ValueError:
            pass

        res = self._wrapper.project.preset(gn,"interaction_directed_monopartite")
        self.assertEqual(gn,res.name())
        
        graph = self._builder.build_projection_graph(res)
        int_der = [str(n[1]["key"]) for n in model.get_derived(interaction)]
        pe_der = [str(n[1]["key"]) for n in model.get_derived(pe)]
        for e in graph.edges():
            n = e.n
            v = e.v
            self.assertIn(n.get_type(),pe_der)
            self.assertIn(v.get_type(),pe_der)
            self.assertIn(e.get_type(),int_der)
        #self._wrapper.project.drop(gn)

    def test_project_interaction_ppi_bi(self):
        model = self._wrapper.model
        ids = self._wrapper.ids
        interaction = ids.objects.interaction
        protein = ids.objects.protein
        gn = "test1"
        try:
            self._wrapper.project.drop(gn)
        except ValueError:
            pass

        res = self._wrapper.project.preset(gn,"interaction_ppi_directed_bipartite")
        self.assertEqual(gn,res.name())
        graph = self._builder.build_projection_graph(res)
        g_info = res._graph_info()
        config = g_info["configuration"]
        rel_proj = config["relationshipProjection"]
        nfilter = config["nodeFilter"]
        efliter = config["relationshipFilter"]
        schema = g_info["schema"]
        int_der = [str(n[1]["key"]) for n in model.get_derived(interaction)]
        pe_der = [str(protein)] + [str(n[1]["key"]) for n in model.get_derived(protein)]
        for e in graph.edges():
            n = e.n
            v = e.v
            self.assertIn(n.get_type(),pe_der)
            self.assertIn(v.get_type(),pe_der)
            self.assertIn(e.get_type(),int_der)
        self._wrapper.project.drop(gn)

    def test_project_interaction_ppi_mono(self):
        model = self._wrapper.model
        ids = self._wrapper.ids
        interaction = ids.objects.interaction
        protein = ids.objects.protein
        gn = "test1"
        try:
            self._wrapper.project.drop(gn)
        except ValueError:
            pass

        res = self._wrapper.project.preset(gn,"interaction_ppi_directed_monopartite")
        self.assertEqual(gn,res.name())
        graph = self._builder.build_projection_graph(res)
        g_info = res._graph_info()
        config = g_info["configuration"]
        rel_proj = config["relationshipProjection"]
        nfilter = config["nodeFilter"]
        efliter = config["relationshipFilter"]
        schema = g_info["schema"]
        int_der = [str(n[1]["key"]) for n in model.get_derived(interaction)]
        pe_der = [str(protein)] + [str(n[1]["key"]) for n in model.get_derived(protein)]
        for e in graph.edges():
            n = e.n
            v = e.v
            self.assertIn(n.get_type(),pe_der)
            self.assertIn(v.get_type(),pe_der)
            self.assertIn(e.get_type(),int_der)
        self._wrapper.project.drop(gn)

    def test_project_interaction_genetic_mono(self):
        model = self._wrapper.model
        ids = self._wrapper.ids
        interaction = ids.objects.interaction
        dna = ids.objects.dna
        gn = "test1"
        try:
            self._wrapper.project.drop(gn)
        except ValueError:
            pass

        res = self._wrapper.project.preset(gn,"interaction_genetic_directed_monopartite")
        self.assertEqual(gn,res.name())
        graph = self._builder.build_projection_graph(res)
        int_der = [str(n[1]["key"]) for n in model.get_derived(interaction)]
        pe_der = [str(dna)] + [str(n[1]["key"]) for n in model.get_derived(dna)]
        for e in graph.edges():
            n = e.n
            v = e.v
            self.assertIn(n.get_type(),pe_der)
            self.assertIn(v.get_type(),pe_der)
            self.assertIn(e.get_type(),int_der)
        self._wrapper.project.drop(gn)

class TestGDSProcedures(unittest.TestCase):
    def setUp(self):
        self._wrapper = NVGraph()
        self._builder = ProjectionBuilder(self._wrapper)
        self._rdf = SBOLGraph(test_fn)
        #self._backup = self._wrapper.get_all_edges()
        #self._wrapper.purge()
        #self._wrapper.add_graph(test_fn)

    def tearDown(self):
        return
        self._wrapper.purge()
        if len(self._backup) > 0:
            for edge in self._backup:
                n = self._wrapper.add_node(edge.n)
                v = self._wrapper.add_node(edge.v)
                self._wrapper.add_edge(n,v,edge)
            self._wrapper.submit()

    def test_mutate(self):
        gn = "test1"
        try:
            self._wrapper.project.drop(gn)
        except ValueError:
            pass
        res = self._wrapper.project.preset(gn,"hierarchy")
        pr = self._wrapper.project.mutate(gn,["1","2","3"],"mut","lab")
        self.assertEqual(len(pr),res.node_count())
        self._wrapper.project.drop(gn)
    
    def test_page_rank(self):
        gn = "test1"
        try:
            self._wrapper.project.drop(gn)
        except ValueError:
            pass
        res = self._wrapper.project.preset(gn,"hierarchy")
        pr = self._wrapper.procedure.centrality.page_rank(gn)
        self.assertEqual(len(pr),res.node_count())
        self._wrapper.project.drop(gn)

    def test_article_rank(self):
        gn = "test1"
        try:
            self._wrapper.project.drop(gn)
        except ValueError:
            pass
        res = self._wrapper.project.preset(gn,"hierarchy")
        pr = self._wrapper.procedure.centrality.article_rank(gn)
        self.assertEqual(len(pr),res.node_count())
        self._wrapper.project.drop(gn)

    def test_eigenvector_centrality(self):
        gn = "test1"
        try:
            self._wrapper.project.drop(gn)
        except ValueError:
            pass
        res = self._wrapper.project.preset(gn,"hierarchy")
        pr = self._wrapper.procedure.centrality.eigenvector(gn)
        self.assertEqual(len(pr),res.node_count())
        self._wrapper.project.drop(gn)

    def test_betweenness_centrality(self):
        gn = "test1"
        try:
            self._wrapper.project.drop(gn)
        except ValueError:
            pass
        res = self._wrapper.project.preset(gn,"hierarchy")
        pr = self._wrapper.procedure.centrality.betweenness(gn)
        self.assertEqual(len(pr),res.node_count())
        self._wrapper.project.drop(gn)

    def test_degree_centrality(self):
        gn = "test1"
        try:
            self._wrapper.project.drop(gn)
        except ValueError:
            pass
        res = self._wrapper.project.preset(gn,"hierarchy")
        pr = self._wrapper.procedure.centrality.degree(gn)
        self.assertEqual(len(pr),res.node_count())
        self._wrapper.project.drop(gn)

    def test_closeness_centrality(self):
        gn = "test1"
        try:
            self._wrapper.project.drop(gn)
        except ValueError:
            pass
        res = self._wrapper.project.preset(gn,"hierarchy")
        pr = self._wrapper.procedure.centrality.closeness(gn)
        self.assertEqual(len(pr),res.node_count())
        self._wrapper.project.drop(gn)

    def test_harmonic_centrality(self):
        gn = "test1"
        try:
            self._wrapper.project.drop(gn)
        except ValueError:
            pass
        res = self._wrapper.project.preset(gn,"hierarchy")
        pr = self._wrapper.procedure.centrality.harmonic(gn)
        self.assertEqual(len(pr),res.node_count())
        self._wrapper.project.drop(gn)

    def test_hits(self):
        gn = "test1"
        try:
            self._wrapper.project.drop(gn)
        except ValueError:
            pass
        res = self._wrapper.project.preset(gn,"hierarchy")
        pr = self._wrapper.procedure.centrality.hits(gn)
        self.assertEqual(len(pr),res.node_count())
        self._wrapper.project.drop(gn)

    def test_celf_influence_maximization(self):
        gn = "test1"
        try:
            self._wrapper.project.drop(gn)
        except ValueError:
            pass
        res = self._wrapper.project.preset(gn,"hierarchy")
        pr = self._wrapper.procedure.centrality.celf_im(gn)
        self.assertEqual(len(pr),3)
        self._wrapper.project.drop(gn)

    def test_greedy_influence_maximization(self):
        gn = "test1"
        try:
            self._wrapper.project.drop(gn)
        except ValueError:
            pass
        res = self._wrapper.project.preset(gn,"hierarchy")
        pr = self._wrapper.procedure.centrality.greedy_im(gn)
        self.assertEqual(len(pr),3)
        self._wrapper.project.drop(gn)

    def test_louvain(self):
        gn = "test1"
        try:
            self._wrapper.project.drop(gn)
        except ValueError:
            pass
        res = self._wrapper.project.preset(gn,"hierarchy")
        pr = self._wrapper.procedure.community_detection.louvain(gn)
        self.assertEqual(len(pr),res.node_count())
        self._wrapper.project.drop(gn)

    def test_label_propagation(self):
        gn = "test1"
        try:
            self._wrapper.project.drop(gn)
        except ValueError:
            pass
        res = self._wrapper.project.preset(gn,"hierarchy")
        pr = self._wrapper.procedure.community_detection.label_propagation(gn)
        self.assertEqual(len(pr),res.node_count())
        self._wrapper.project.drop(gn)

    def test_wcc(self):
        gn = "test1"
        try:
            self._wrapper.project.drop(gn)
        except ValueError:
            pass
        res = self._wrapper.project.preset(gn,"hierarchy")
        pr = self._wrapper.procedure.community_detection.wcc(gn)
        self.assertEqual(len(pr),res.node_count())
        self._wrapper.project.drop(gn)
               
    def test_triangle_count(self):
        gn = "test1"
        try:
            self._wrapper.project.drop(gn)
        except ValueError:
            pass
        res = self._wrapper.project.preset(gn,"hierarchy")
        pr = self._wrapper.procedure.community_detection.triangle_count(gn)
        self.assertEqual(len(pr),res.node_count())
        self._wrapper.project.drop(gn)
               
    def test_local_clustering_coefficient(self):
        gn = "test1"
        try:
            self._wrapper.project.drop(gn)
        except ValueError:
            pass
        res = self._wrapper.project.preset(gn,"hierarchy")
        pr = self._wrapper.procedure.community_detection.local_clustering_coefficient(gn)
        self.assertEqual(len(pr),res.node_count())
        self._wrapper.project.drop(gn)
               
    def test_k1coloring(self):
        gn = "test1"
        try:
            self._wrapper.project.drop(gn)
        except ValueError:
            pass
        res = self._wrapper.project.preset(gn,"hierarchy")
        pr = self._wrapper.procedure.community_detection.k1coloring(gn)
        self.assertEqual(len(pr),res.node_count())
        self._wrapper.project.drop(gn)
               
    def test_modularity_optimization(self):
        gn = "test1"
        try:
            self._wrapper.project.drop(gn)
        except ValueError:
            pass
        res = self._wrapper.project.preset(gn,"hierarchy")
        pr = self._wrapper.procedure.community_detection.modularity_optimization(gn)
        self.assertEqual(len(pr),res.node_count())
        self._wrapper.project.drop(gn)
               
    def test_scc(self):
        gn = "test1"
        try:
            self._wrapper.project.drop(gn)
        except ValueError:
            pass
        res = self._wrapper.project.preset(gn,"hierarchy")
        pr = self._wrapper.procedure.community_detection.scc(gn)
        self.assertEqual(len(pr),res.node_count())
        self._wrapper.project.drop(gn)

    def test_sllpa(self):
        gn = "test1"
        try:
            self._wrapper.project.drop(gn)
        except ValueError:
            pass
        res = self._wrapper.project.preset(gn,"hierarchy")
        pr = self._wrapper.procedure.community_detection.sllpa(gn)
        self.assertEqual(len(pr),res.node_count())
        self._wrapper.project.drop(gn)
               
    
    def test_maxkcut(self):
        gn = "test1"
        try:
            self._wrapper.project.drop(gn)
        except ValueError:
            pass
        res = self._wrapper.project.preset(gn,"hierarchy")
        pr = self._wrapper.procedure.community_detection.maxkcut(gn)
        self.assertEqual(len(pr),res.node_count())
        self._wrapper.project.drop(gn)


    def test_node_similarity(self):
        gn = "test1"
        try:
            self._wrapper.project.drop(gn)
        except ValueError:
            pass
        res = self._wrapper.project.preset(gn,"hierarchy")
        pr = self._wrapper.procedure.similarity.node(gn)
        self.assertEqual(len(pr),res.node_count())
        self._wrapper.project.drop(gn)
    
    def test_delta_all_shortest_paths(self):
        gn = "test1"
        try:
            self._wrapper.project.drop(gn)
        except ValueError:
            pass
        res = self._wrapper.project.preset(gn,"hierarchy")
        g = self._builder.build_projection_graph(res)
        nodes = [*g.nodes()]
        pr = self._wrapper.procedure.path_finding.delta_asp(gn,nodes[0].get_key())
        self.assertTrue(len(pr)>1)
        for path in pr:
            self.assertIn("path",path)
            self.assertIn("totalCost",path)
            self.assertIsInstance(path["totalCost"],float)
            self.assertIsInstance(path["path"],list)
        self._wrapper.project.drop(gn)

    def test_dijkstra_all_shortest_paths(self):
        gn = "test1"
        try:
            self._wrapper.project.drop(gn)
        except ValueError:
            pass
        res = self._wrapper.project.preset(gn,"hierarchy")
        g = self._builder.build_projection_graph(res)
        nodes = [*g.nodes()]
        pr = self._wrapper.procedure.path_finding.dijkstra_asp(gn,nodes[0].get_key())
        self.assertTrue(len(pr)>0)
        for path in pr:
            self.assertIn("path",path)
            self.assertIn("totalCost",path)
            self.assertIsInstance(path["totalCost"],float)
            self.assertIsInstance(path["path"],list)
        self._wrapper.project.drop(gn)

    def test_dijkstra_shortest_path(self):
        gn = "test1"
        try:
            self._wrapper.project.drop(gn)
        except ValueError:
            pass
        res = self._wrapper.project.preset(gn,"hierarchy")
        g = self._builder.build_projection_graph(res)
        nodes = [*g.nodes()]
        pr = self._wrapper.procedure.path_finding.dijkstra_sp(gn,nodes[0].get_key(),nodes[1].get_key())
        self.assertTrue(len(pr) == 1)
        pr = pr[0]
        pr = pr["path"]
        self.assertCountEqual([r.get_key() for r in pr],[nodes[0].get_key(),nodes[1].get_key()])
        self._wrapper.project.drop(gn)

    def test_yens_shortest_path(self):
        gn = "test1"
        try:
            self._wrapper.project.drop(gn)
        except ValueError:
            pass
        res = self._wrapper.project.preset(gn,"hierarchy")
        g = self._builder.build_projection_graph(res)
        nodes = [*g.nodes()]
        pr = self._wrapper.procedure.path_finding.yens_sp(gn,nodes[0].get_key(),nodes[1].get_key(),7)
        self.assertTrue(len(pr) == 1)
        pr = pr[0]
        pr = pr["path"]
        self.assertCountEqual([r.get_key() for r in pr],[nodes[0].get_key(),nodes[1].get_key()])
        self._wrapper.project.drop(gn)

    def test_bfs(self):
        gn = "test1"
        try:
            self._wrapper.project.drop(gn)
        except ValueError:
            pass
        res = self._wrapper.project.preset(gn,"hierarchy")
        g = self._builder.build_projection_graph(res)
        nodes = [*g.nodes()]
        pr = self._wrapper.procedure.path_finding.bfs(gn,nodes[0].get_key(),nodes[1].get_key())
        for p in pr:
            pr = p["path"]
            self.assertCountEqual([r.get_key() for r in pr],[nodes[0].get_key(),nodes[1].get_key()])
        self._wrapper.project.drop(gn)

    def test_dfs(self):
        gn = "test1"
        try:
            self._wrapper.project.drop(gn)
        except ValueError:
            pass
        res = self._wrapper.project.preset(gn,"hierarchy")
        g = self._builder.build_projection_graph(res)
        nodes = [*g.nodes()]
        pr = self._wrapper.procedure.path_finding.dfs(gn,nodes[0].get_key(),nodes[1].get_key())
        for p in pr:
            self.assertEqual(nodes[0],p["path"][0])
            self.assertEqual(nodes[1],p["path"][-1])
        self._wrapper.project.drop(gn)


    def test_adamic_adar(self):
        gn = "test1"
        try:
            self._wrapper.project.drop(gn)
        except ValueError:
            pass
        res = self._wrapper.project.preset(gn,"hierarchy")
        g = self._builder.build_projection_graph(res)
        nodes = [*g.nodes()]
        pr = self._wrapper.procedure.tpp.adamic_adar(gn,nodes[0].get_key(),nodes[1].get_key())
        self._wrapper.project.drop(gn)
