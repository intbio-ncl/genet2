import sys
import os
import unittest
from rdflib import DCTERMS,URIRef
from pysbolgraph.SBOL2Serialize import serialize_sboll2
from pysbolgraph.SBOL2Graph import SBOL2Graph
from shutil import copyfile

sys.path.insert(0, os.path.join(".."))
sys.path.insert(0, os.path.join("..",".."))
sys.path.insert(0, os.path.join("..","..",".."))
sys.path.insert(0, os.path.join("..","..","..",".."))
sys.path.insert(0, os.path.join("..","..","..","..",".."))
from app.converter.sbol_convert import convert,export
from app.graph.world_graph import WorldGraph
from app.converter.utility.graph import SBOLGraph
from app.graph.utility.graph_objects.node import Node
from app.graph.utility.model.model import model
from app.converter.utility.identifiers import identifiers
from app.visualiser.builder.editor import EditorBuilder


curr_dir = os.path.dirname(os.path.realpath(__file__))
ids = model.identifiers
nor_fn = os.path.join("..","files","nor_full.xml")
class TestExport(unittest.TestCase):
    def setUp(self):
        copyfile(nor_fn, nor_fn+"_copy")

    def tearDown(self):
        copyfile(nor_fn+"_copy",nor_fn)
        os.remove(nor_fn+"_copy")

    def test_no_changes(self):
        fn = os.path.join("..","files","nor_full.xml")
        pre_graph = SBOLGraph(fn)
        gn = "test_no_changes"
        graph = WorldGraph()
        convert(fn,graph.driver,gn)
        dg = graph.get_design(gn)
        out_fn = export(fn,gn)
        post_graph = SBOLGraph(out_fn)
        self.assertEqual(len(pre_graph),len(post_graph))
        dg.drop()

    def test_add_physical_entity(self):
        fn = os.path.join("..","files","empty_graph.xml")
        gn = ["test_no_changes"]
        graph = WorldGraph()
        graph.remove_design(gn[0])
        convert(fn,graph.driver,gn[0])
        dg = graph.get_design(gn)
        properties = {str(DCTERMS.description) : "test_desc"}
        i_seq = "ATCG"
        node_id = "https://synbiohub.org/public/igem/BBa_R00102345/1"
        dg.add_node(node_id,ids.objects.cds,sequence=i_seq,**properties)
        out_fn = export(fn,gn)
        post_graph = SBOLGraph(out_fn)

        cds = post_graph.get_component_definitions()
        self.assertEqual(len(cds),1)
        cds = cds[0]
        self.assertEqual(str(cds),node_id)
        self.assertEqual(post_graph.get_types(cds),[identifiers.roles.DNA])
        self.assertEqual(post_graph.get_roles(cds),[identifiers.roles.cds])
        seq = post_graph.get_sequence_names(cds)
        self.assertEqual(len(seq) , 1)
        seq_seq = post_graph.get_sequences(sequence_names=seq)
        self.assertEqual([str(s) for s in seq_seq],["ATCG"])

        node_id = "https://synbiohub.org/public/igem/BBa_R00102345678/1"
        dg.add_node(node_id,ids.objects.dna,sequence=i_seq,**properties)
        out_fn = export(fn,gn)
        post_graph = SBOLGraph(out_fn)
        t = post_graph.get_rdf_type(URIRef(node_id))
        self.assertEqual(t,identifiers.objects.component_definition)

        del_graph = SBOLGraph()
        pysbolG = SBOL2Graph()
        pysbolG += del_graph
        sbol = serialize_sboll2(pysbolG).decode("utf-8")
        with open(fn, 'w') as o:
            o.write(sbol)
        dg.drop()

    def test_add_conceptual_entity(self):
        fn = os.path.join("..","files","empty_graph.xml")
        gn = ["test_no_changes"]
        graph = WorldGraph()
        graph.remove_design(gn[0])
        convert(fn,graph.driver,gn[0])
        dg = graph.get_design(gn)
        node_id = "https://synbiohub.org/public/igem/inter/1"
        dg.add_node(node_id,ids.objects.repression)
        out_fn = export(fn,gn)
        post_graph = SBOLGraph(out_fn)
        ints = post_graph.get_interactions()
        self.assertEqual(len(ints),1)
        ints = ints[0]
        self.assertEqual(str(ints),node_id)
        self.assertEqual(post_graph.get_types(ints),[identifiers.roles.inhibition])
        del_graph = SBOLGraph()
        pysbolG = SBOL2Graph()
        pysbolG += del_graph
        sbol = serialize_sboll2(pysbolG).decode("utf-8")
        with open(fn, 'w') as o:
            o.write(sbol)
        dg.drop()

    def test_remove_physical_entity(self):
        fn = os.path.join("..","files","empty_graph.xml")
        gn = ["test_no_changes"]
        graph = WorldGraph()
        graph.remove_design(gn[0])
        convert(fn,graph.driver,gn[0])
        dg = graph.get_design(gn)
        properties = {str(DCTERMS.description) : "test_desc"}
        i_seq = "ATCG"
        node_id = "https://synbiohub.org/public/igem/BBa_R00102345/1"
        dg.add_node(node_id,ids.objects.cds,sequence=i_seq,**properties)
        node = Node(node_id,ids.objects.cds)
        dg.remove_node(node)
        out_fn = export(fn,gn)
        post_graph = SBOLGraph(out_fn)
        cds = post_graph.get_component_definitions()
        self.assertEqual(len(cds),0)
        seqs = post_graph.get_sequence_names(None)
        self.assertEqual(len(seqs),0)
        del_graph = SBOLGraph()
        pysbolG = SBOL2Graph()
        pysbolG += del_graph
        sbol = serialize_sboll2(pysbolG).decode("utf-8")
        with open(fn, 'w') as o:
            o.write(sbol)
        dg.drop()

    def test_remove_conceptual_entity(self):
        fn = os.path.join("..","files","empty_graph.xml")
        gn = ["test_no_changes"]
        graph = WorldGraph()
        graph.remove_design(gn[0])
        convert(fn,graph.driver,gn[0])
        dg = graph.get_design(gn)
        node_id = "https://synbiohub.org/public/igem/inter/1"
        dg.add_node(node_id,ids.objects.repression)
        node = Node(node_id,ids.objects.repression)
        dg.remove_node(node)
        out_fn = export(fn,gn)
        post_graph = SBOLGraph(out_fn)
        ints = post_graph.get_interactions()
        self.assertEqual(len(ints),0)
        del_graph = SBOLGraph()
        pysbolG = SBOL2Graph()
        pysbolG += del_graph
        sbol = serialize_sboll2(pysbolG).decode("utf-8")
        with open(fn, 'w') as o:
            o.write(sbol)
        dg.drop()

    def test_replace_node_label(self):
        fn = os.path.join("..","files","empty_graph.xml")
        gn = ["test_no_changes"]
        graph = WorldGraph()
        graph.remove_design(gn[0])
        convert(fn,graph.driver,gn[0])
        dg = graph.get_design(gn)
        properties = {str(DCTERMS.description) : "test_desc"}
        i_seq = "ATCG"
        node_id = "https://synbiohub.org/public/igem/BBa_R00102345/1"
        dg.add_node(node_id,ids.objects.cds,sequence=i_seq,**properties)
        new_id = "https://synbiohub.org/public/igem/BBa_R00102345_new_id/1"
        dg.replace_label(node_id,new_id)
        out_fn = export(fn,gn)
        post_graph = SBOLGraph(out_fn)
        cds = post_graph.get_component_definitions()
        self.assertEqual(len(cds),1)
        self.assertEqual(str(cds[0]),new_id)

        del_graph = SBOLGraph()
        pysbolG = SBOL2Graph()
        pysbolG += del_graph
        sbol = serialize_sboll2(pysbolG).decode("utf-8")
        with open(fn, 'w') as o:
            o.write(sbol)
        dg.drop()

    def test_replace_node_properties(self):
        fn = os.path.join("..","files","empty_graph.xml")
        gn = ["test_no_changes"]
        graph = WorldGraph()
        graph.remove_design(gn[0])
        convert(fn,graph.driver,gn[0])
        dg = graph.get_design(gn)
        properties = {str(DCTERMS.description) : "test_desc"}
        i_seq = "ATCG"
        node_id = "https://synbiohub.org/public/igem/BBa_R00102345/1"
        dg.add_node(node_id,ids.objects.cds,sequence=i_seq,**properties)
        new_seq = "GCAT"
        node = Node(node_id,ids.objects.cds)
        dg.replace_node_property(node,model.identifiers.predicates.has_sequence,new_seq)
        out_fn = export(fn,gn)
        post_graph = SBOLGraph(out_fn)
        cds = post_graph.get_component_definitions()
        self.assertEqual(len(cds),1)
        self.assertEqual(str(post_graph.get_sequences(cds[0])[0]),new_seq)

        del_graph = SBOLGraph()
        pysbolG = SBOL2Graph()
        pysbolG += del_graph
        sbol = serialize_sboll2(pysbolG).decode("utf-8")
        with open(fn, 'w') as o:
            o.write(sbol)
        dg.drop()

    def test_add_hasPart(self):
        fn = os.path.join("..","files","empty_graph.xml")
        gn = ["test_no_changes"]
        graph = WorldGraph()
        graph.remove_design(gn[0])
        convert(fn,graph.driver,gn[0])
        dg = graph.get_design(gn)

        n1k = URIRef("https://synbiohub.org/public/igem/n1/1")
        n2k = URIRef("https://synbiohub.org/public/igem/n2/1")
        node1 = Node(n1k,model.identifiers.objects.dna,graph_name=gn)
        node2 = Node(n2k,model.identifiers.objects.dna,graph_name=gn)
        edge_key = model.identifiers.predicates.has_part
        edge = (node1,node2,edge_key,{"graph_name":gn})
        dg.add_edges([edge])
        out_fn = export(fn,gn)
        post_graph = SBOLGraph(out_fn)

        n1_t = post_graph.get_rdf_type(n1k)
        self.assertEqual(n1_t,identifiers.objects.component_definition)
        comps = post_graph.get_components(n1k)
        self.assertEqual(len(comps),1)
        defin = post_graph.get_definition(comps[0])
        self.assertEqual(defin,n2k)

        del_graph = SBOLGraph()
        pysbolG = SBOL2Graph()
        pysbolG += del_graph
        sbol = serialize_sboll2(pysbolG).decode("utf-8")
        with open(fn, 'w') as o:
            o.write(sbol)
        dg.drop()

    def test_add_interaction_parts(self):
        fn = os.path.join("..","files","empty_graph.xml")
        gn = ["test_no_changes"]
        graph = WorldGraph()
        graph.remove_design(gn[0])
        convert(fn,graph.driver,gn[0])
        dg = graph.get_design(gn)
        n1k = URIRef("https://synbiohub.org/public/igem/activation/1")
        n2k = URIRef("https://synbiohub.org/public/igem/activated/1")
        node1 = Node(n1k,model.identifiers.objects.activation,graph_name=gn)
        node2 = Node(n2k,model.identifiers.objects.dna,graph_name=gn)
        edge_key = model.identifiers.predicates.activated
        edge = (node1,node2,edge_key,{"graph_name":gn})
        dg.add_edges([edge])
        out_fn = export(fn,gn)
        post_graph = SBOLGraph(out_fn)

        ints = post_graph.get_interactions()
        self.assertEqual(len(ints),1)
        ints = ints[0]
        self.assertEqual(ints,n1k)
        parts = post_graph.get_participants(interaction=ints)
        fc = post_graph.get_participant(parts[0])
        cd = post_graph.get_definition(fc)
        self.assertEqual(cd,n2k)
        md = post_graph.get_module_definition(interaction=ints)
        self.assertIsNotNone(md)

        del_graph = SBOLGraph()
        pysbolG = SBOL2Graph()
        pysbolG += del_graph
        sbol = serialize_sboll2(pysbolG).decode("utf-8")
        with open(fn, 'w') as o:
            o.write(sbol)
        dg.drop()

    def test_add_interaction(self):
        fn = os.path.join("..","files","empty_graph.xml")
        gn = ["test_no_changes"]
        graph = WorldGraph()
        graph.remove_design(gn[0])
        convert(fn,graph.driver,gn[0])
        dg = graph.get_design(gn)
        n1k = URIRef("https://synbiohub.org/public/igem/activation/1")
        n2k = URIRef("https://synbiohub.org/public/igem/activated/1")
        n3k = URIRef("https://synbiohub.org/public/igem/activator/1")
        node1 = Node(n1k,model.identifiers.objects.activation,graph_name=gn)
        node2 = Node(n2k,model.identifiers.objects.dna,graph_name=gn)
        node3 = Node(n3k,model.identifiers.objects.dna,graph_name=gn)

        edge_key = model.identifiers.predicates.activated
        edge1 = (node1,node2,edge_key,{"graph_name":gn})
        edge2 = (node1,node3,edge_key,{"graph_name":gn})
        dg.add_edges([edge1,edge2])
        out_fn = export(fn,gn)
        post_graph = SBOLGraph(out_fn)

        ints = post_graph.get_interactions()
        self.assertEqual(len(ints),1)
        ints = ints[0]
        mds = post_graph.get_module_definition()
        self.assertEqual(ints,n1k)
        for part in post_graph.get_participants(interaction=ints):
            fc = post_graph.get_participant(part)
            cd = post_graph.get_definition(fc)
            self.assertTrue(cd == n2k or cd == n3k)
            md = post_graph.get_module_definition(interaction=ints)
            self.assertEqual(mds,[md])

        del_graph = SBOLGraph()
        pysbolG = SBOL2Graph()
        pysbolG += del_graph
        sbol = serialize_sboll2(pysbolG).decode("utf-8")
        with open(fn, 'w') as o:
            o.write(sbol)
        dg.drop()
    
    def test_remove_edge_has_part(self):
        fn = os.path.join("..","files","empty_graph.xml")
        gn = ["test_no_changes"]
        graph = WorldGraph()
        graph.remove_design(gn[0])
        convert(fn,graph.driver,gn[0])
        dg = graph.get_design(gn)

        n1k = URIRef("https://synbiohub.org/public/igem/n1/1")
        n2k = URIRef("https://synbiohub.org/public/igem/n2/1")
        node1 = Node(n1k,model.identifiers.objects.dna,graph_name=gn)
        node2 = Node(n2k,model.identifiers.objects.dna,graph_name=gn)
        edge_key = model.identifiers.predicates.has_part
        edge = (node1,node2,edge_key,{"graph_name":gn})
        dg.add_edges([edge])
        dg.remove_edges([edge])
        out_fn = export(fn,gn)
        post_graph = SBOLGraph(out_fn)

        n1_t = post_graph.get_rdf_type(n1k)
        self.assertEqual(n1_t,identifiers.objects.component_definition)
        comps = post_graph.get_components(n1k)
        self.assertEqual(len(comps),0)
        del_graph = SBOLGraph()
        pysbolG = SBOL2Graph()
        pysbolG += del_graph
        sbol = serialize_sboll2(pysbolG).decode("utf-8")
        with open(fn, 'w') as o:
            o.write(sbol)
        dg.drop()

    def test_remove_edge_interaction(self):
        fn = os.path.join("..","files","empty_graph.xml")
        gn = ["test_no_changes"]
        graph = WorldGraph()
        graph.remove_design(gn[0])
        convert(fn,graph.driver,gn[0])
        dg = graph.get_design(gn)
        n1k = URIRef("https://synbiohub.org/public/igem/activation/1")
        n2k = URIRef("https://synbiohub.org/public/igem/activated/1")
        n3k = URIRef("https://synbiohub.org/public/igem/activator/1")
        node1 = Node(n1k,model.identifiers.objects.activation,graph_name=gn)
        node2 = Node(n2k,model.identifiers.objects.dna,graph_name=gn)
        node3 = Node(n3k,model.identifiers.objects.dna,graph_name=gn)

        edge_key = model.identifiers.predicates.activated
        edge1 = (node1,node2,edge_key,{"graph_name":gn})
        edge2 = (node1,node3,edge_key,{"graph_name":gn})
        dg.add_edges([edge1,edge2])
        out_fn = export(fn,gn)
        dg.remove_edges([edge1])
        out_fn = export(fn,gn)
        post_graph = SBOLGraph(out_fn)

        ints = post_graph.get_interactions()
        self.assertEqual(len(ints),1)
        ints = ints[0]
        mds = post_graph.get_module_definition()
        self.assertEqual(ints,n1k)
        parts = post_graph.get_participants(interaction=ints)
        self.assertEqual(len(parts),1)
        for part in post_graph.get_participants(interaction=ints):
            fc = post_graph.get_participant(part)
            cd = post_graph.get_definition(fc)
            self.assertTrue(cd == n2k or cd == n3k)
            md = post_graph.get_module_definition(interaction=ints)
            self.assertEqual(mds,[md])

        del_graph = SBOLGraph()
        pysbolG = SBOL2Graph()
        pysbolG += del_graph
        sbol = serialize_sboll2(pysbolG).decode("utf-8")
        with open(fn, 'w') as o:
            o.write(sbol)
        dg.drop()

    def test_edit_design(self): 
        gn = ["test_no_changes"]
        graph = WorldGraph()
        graph.remove_design(gn[0])
        convert(nor_fn,graph.driver,gn[0])
        dg = graph.get_design(gn)

        vis_ed = EditorBuilder(graph)
        vis_ed.set_design(dg)
        vis_ed.set_hierarchy_view()
        vis_ed.build()
        pes = dg.get_physicalentity()
        en1 = pes[0]
        en2 = pes[5]
        nn1 = Node("https://test/n1",model.identifiers.objects.dna)

        n = {'subject': en1.get_key()}
        v = {'object':  en2.get_key()}
        e = "http://www.nv_ontology.org/hasPart"
        vis_ed.add_edges(n,v,e)
        vis_ed.add_node(nn1.get_key(),nn1.get_type())
        vis_ed.add_edges({"subject":nn1},v,e)

        vis_ed.set_interaction_view()
        vis_ed.build()

        vn = vis_ed.get_view_nodes()
        en3 = vn[0]
        en4 = vn[-2]
        n = {"http://www.nv_ontology.org/repressor" : en3.get_key()}
        v = {"http://www.nv_ontology.org/repressed" : en4.get_key()}
        e = "http://www.nv_ontology.org/Repression"
        vis_ed.add_edges(n,v,e)

        rl1 = "https://test/new_label1/1"
        rl2 = "https://test/new_label2/1"
        dg.replace_label(en3.get_key(),rl1)
        dg.replace_label(nn1.get_key(),rl2)
        en3.key = rl1
        nn1.key = rl2

        vis_ed.set_interaction_protein_view()
        vis_ed.build()
        vn = vis_ed.get_view_nodes()
        en5 = vn[0]
        en6 = vn[-1]
        pn = {"http://www.nv_ontology.org/activator" : en5.get_key()}
        pv = {"http://www.nv_ontology.org/activated" : en6.get_key()}
        pe = "http://www.nv_ontology.org/Activation"
        vis_ed.add_edges(pn,pv,pe)

        pre_graph = SBOLGraph(nor_fn)
        out_fn = export(nor_fn,gn)
        post_graph = SBOLGraph(nor_fn)
        d_graph = post_graph - pre_graph
        cds = d_graph.get_component_definitions()
        self.assertCountEqual(cds,[URIRef(nn1.get_key()),URIRef(en3.get_key())])
        cds_t = [d_graph.get_types(c) for c in cds]
        self.assertCountEqual(cds_t,[[identifiers.roles.DNA],[identifiers.roles.DNARegion]])
        for c in d_graph.get_components(URIRef(pes[0].get_key())):
            self.assertEqual(URIRef(en2.get_key()),post_graph.get_definition(c))
        for c in d_graph.get_components(URIRef(nn1.get_key())):
            self.assertEqual(URIRef(en2.get_key()),post_graph.get_definition(c))
        for i in d_graph.get_interactions():
            if d_graph.get_types(i) == [identifiers.roles.stimulation]:
                parts = d_graph.get_participants(interaction=i)
                fcs = [d_graph.get_participant(p) for p in parts]
                self.assertEqual(len(parts),2)
                self.assertEqual(len(fcs),2)
                e_defs = [pre_graph.get_definition(f) for f in fcs]
                n_defs = [d_graph.get_definition(f) for f in fcs]
                e_defs = [f for f in e_defs if f is not None]
                n_defs = [f for f in n_defs if f is not None]
                self.assertEqual(n_defs,[])
                self.assertCountEqual(e_defs,[URIRef(en5.get_key()),URIRef("http://shortbol.org/v2#CI_p/1")])

            elif d_graph.get_types(i) == [identifiers.roles.inhibition]:
                parts = d_graph.get_participants(interaction=i)
                fcs = [d_graph.get_participant(p) for p in parts]
                self.assertEqual(len(parts),2)
                self.assertEqual(len(fcs),2)
                e_defs = [pre_graph.get_definition(f) for f in fcs]
                n_defs = [d_graph.get_definition(f) for f in fcs]
                e_defs = [f for f in e_defs if f is not None]
                n_defs = [f for f in n_defs if f is not None]
                self.assertEqual(e_defs,[])
                self.assertCountEqual(n_defs,[URIRef(en4.get_key()),URIRef(en3.get_key())])
        #dg.drop()
