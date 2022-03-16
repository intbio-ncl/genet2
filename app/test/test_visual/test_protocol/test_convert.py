import unittest
import os
import sys
import re
import json

from rdflib import RDF
from opentrons.simulate import simulate
sys.path.insert(0, os.path.join(".."))
sys.path.insert(0, os.path.join("..",".."))
sys.path.insert(0, os.path.join("..","..",".."))

from converters.protocol_handler import convert as protocol_convert
from converters.model_handler import convert as model_convert

curr_dir = os.path.dirname(os.path.realpath(__file__))
model_fn = os.path.join(curr_dir,"..","..","utility","nv_protocol.xml")
test_dir = os.path.join(curr_dir,"..","files")

class TestConvertOT2(unittest.TestCase):

    def setUp(self):
        None

    def tearDown(self):
        None

    def run_action_test(self,graph,action,model,protocol,protocol_edges):
        prot_id,prot_data = protocol
        nv_actions = model.identifiers.predicates.actions
        nv_source = model.identifiers.predicates.source
        nv_dest = model.identifiers.predicates.destination
        nv_container = model.identifiers.objects.container
        nv_well = model.identifiers.objects.well
        nv_hasContainer = model.identifiers.predicates.has_container

        source = [c[1] for c in graph.search((action,nv_source,None))]
        dest = [c[1] for c in graph.search((action,nv_dest,None))]
        sub_actions = [c[1] for c in graph.search((action,nv_actions,None))]


        for s_action in sub_actions:
            s_action_id,s_action_data = s_action
            for act_id,act_data in resolve_action(graph,s_action_id):
                self.run_action_test(graph,act_id,model,protocol,protocol_edges)

        if source != []:
            self.assertEqual(len(source),1)
            s_id,s_data = source[0]
            source = graph.search((s_id,RDF.type,None))[0]
            self.assertTrue(source[1][1]["key"]==nv_container or source[1][1]["key"]==nv_well)
            source_parent = graph.search((None,nv_hasContainer,source[0][0]))
            if source_parent != []:
                source = source_parent[0][0]
            container_trip = ([prot_id,prot_data],source,nv_hasContainer)
            self.assertIn(container_trip,protocol_edges)
            
        if dest != []:
            self.assertEqual(len(dest),1)
            s_id,s_data = dest[0]
            dest = graph.search((s_id,RDF.type,None))[0]
            self.assertTrue(dest[1][1]["key"]==nv_container or dest[1][1]["key"]==nv_well)
            dest_parent = graph.search((None,nv_hasContainer,dest[0][0]))
            if dest_parent != []:
                dest = dest_parent[0][0]
            container_trip = ([prot_id,prot_data],dest,nv_hasContainer)
            self.assertIn(container_trip,protocol_edges)

    def run_container_test(self,graph,container,model,protocol,protocol_edges):
        # No meaningful tests yet.
        pass

    def run_instrument_test(self,graph,action,model,protocol,protocol_edges):
        # No meaningful tests yet.
        pass

    def test_layer0(self):
        filename = os.path.join(test_dir,"protocols","opentrons","ot2_layer0.py")
        model = model_convert(model_fn)
        nv_action = model.identifiers.objects.action
        nv_actions = model.identifiers.predicates.actions
        nv_source = model.identifiers.predicates.source
        nv_dest = model.identifiers.predicates.destination
        nv_protocol = model.identifiers.objects.protocol
        nv_container = model.identifiers.objects.container
        nv_well = model.identifiers.objects.well
        nv_hasContainer = model.identifiers.predicates.has_container
         
        classes = [c[1]["key"] for c in model.get_classes(False)]
        graph = protocol_convert(model,filename)

        protocol = [c[0] for c in graph.search((None,RDF.type,nv_protocol))]
        self.assertEqual(len(protocol),1)
        prot_id,prot_data = protocol[0]
        protocol_edges = graph.search((prot_id,None,None))

        for n,v,e in graph.search((None,RDF.type,None)):
            n,n_data = n
            v,v_data = v
            self.assertIn(v_data["key"],classes)
            if model.is_derived(v_data["key"],nv_action):
                self.assertEqual(len(graph.search((n,nv_actions,None))),0)
                source = [c[1] for c in graph.search((n,nv_source,None))]
                dest = [c[1] for c in graph.search((n,nv_dest,None))]
                if source != []:
                    self.assertEqual(len(source),1)
                    s_id,s_data = source[0]
                    source = graph.search((s_id,RDF.type,None))[0]
                    self.assertTrue(source[1][1]["key"] == nv_container or source[1][1]["key"]== nv_well)
                    source_parent = graph.search((None,nv_hasContainer,source[0][0]))
                    if source_parent != []:
                        source = source_parent[0][0]
                    container_trip = ([prot_id,prot_data],source,nv_hasContainer)
                    self.assertIn(container_trip,protocol_edges)
                if dest != []:
                    self.assertEqual(len(dest),1)
                    s_id,s_data = dest[0]
                    dest = graph.search((s_id,RDF.type,None))[0]
                    self.assertTrue(dest[1][1]["key"]==nv_container or dest[1][1]["key"]== nv_well)
                    dest_parent = graph.search((None,nv_hasContainer,dest[0][0]))
                    if dest_parent != []:
                        dest = dest_parent[0][0]
                    container_trip = ([prot_id,prot_data],dest,nv_hasContainer)
                    self.assertIn(container_trip,protocol_edges)

    def test_layer1(self):
        filename = os.path.join(test_dir,"protocols","opentrons","ot2_layer1.py")
        model = model_convert(model_fn)
        nv_action = model.identifiers.objects.action
        nv_protocol = model.identifiers.objects.protocol
        nv_container = model.identifiers.objects.container
        nv_instrument = model.identifiers.objects.instrument
         
        classes = [c[1]["key"] for c in model.get_classes(False)]
        graph = protocol_convert(model,filename)

        protocol = [c[0] for c in graph.search((None,RDF.type,nv_protocol))]
        self.assertEqual(len(protocol),1)
        prot_id,prot_data = protocol[0]
        protocol_edges = graph.search((prot_id,None,None))

        for n,v,e in graph.search((None,RDF.type,None)):
            n,n_data = n
            v,v_data = v
            self.assertIn(v_data["key"],classes)
            if model.is_derived(v_data["key"],nv_action):
                self.run_action_test(graph,n,model,protocol[0],protocol_edges)
            
            elif model.is_derived(v_data["key"],nv_container):
                self.run_container_test(graph,n,model,protocol[0],protocol_edges)

            elif model.is_derived(v_data["key"],nv_instrument):
                self.run_instrument_test(graph,n,model,protocol[0],protocol_edges)

    def test_layer_mixed(self):
        filename = os.path.join(test_dir,"protocols","opentrons","ot2_layer_mixed.py")
        model = model_convert(model_fn)
        nv_action = model.identifiers.objects.action
        nv_actions = model.identifiers.predicates.actions
        nv_protocol = model.identifiers.objects.protocol
        nv_container = model.identifiers.objects.container
        nv_instrument = model.identifiers.objects.instrument
         
        classes = [c[1]["key"] for c in model.get_classes(False)]
        graph = protocol_convert(model,filename)

        protocol = [c[0] for c in graph.search((None,RDF.type,nv_protocol))]
        self.assertEqual(len(protocol),1)
        prot_id,prot_data = protocol[0]
        protocol_edges = graph.search((prot_id,None,None))

        for n,v,e in graph.search((None,RDF.type,None)):
            n,n_data = n
            v,v_data = v
            self.assertIn(v_data["key"],classes)
            if model.is_derived(v_data["key"],nv_action):
                self.run_action_test(graph,n,model,protocol[0],protocol_edges)
            
            elif model.is_derived(v_data["key"],nv_container):
                self.run_container_test(graph,n,model,protocol[0],protocol_edges)

            elif model.is_derived(v_data["key"],nv_instrument):
                self.run_instrument_test(graph,n,model,protocol[0],protocol_edges)


        protocol_file = open(filename)
        runlog, _bundle = simulate(protocol_file)
        action = graph.search((prot_id,nv_actions,None))[0][1][0]
        def _run(action):
            a_id,a_data = action
            runlog_element = runlog.pop(0)
            rl_pl = runlog_element["payload"]
            rl_text = rl_pl["text"]
            self.assertEqual(_get_name(a_data["key"]).split("-")[0].lower(),rl_text.split()[0].lower(),rl_text) 
            sa = graph.search((a_id,nv_actions,None))
            if len(sa) > 1:
                self.fail()
            if len(sa) != 1:
                return
            for sa in resolve_action(graph,sa[0][1][0]):
                _run(sa)

        actions = resolve_action(graph,action)
        for index,action in enumerate(actions):
            _run(action)

    def test_layer_complex(self):
        filename = os.path.join(test_dir,"protocols","opentrons","1_clip.ot2.py")
        model = model_convert(model_fn)
        nv_actions = model.identifiers.predicates.actions
        nv_action = model.identifiers.objects.action
        nv_protocol = model.identifiers.objects.protocol
        nv_container = model.identifiers.objects.container
        nv_instrument = model.identifiers.objects.instrument
         
        classes = [c[1]["key"] for c in model.get_classes(False)]
        graph = protocol_convert(model,filename)

        protocol = [c[0] for c in graph.search((None,RDF.type,nv_protocol))]
        self.assertEqual(len(protocol),1)
        prot_id,prot_data = protocol[0]
        protocol_edges = graph.search((prot_id,None,None))

        for n,v,e in graph.search((None,RDF.type,None)):
            n,n_data = n
            v,v_data = v
            self.assertIn(v_data["key"],classes)
            if model.is_derived(v_data["key"],nv_action):
                self.run_action_test(graph,n,model,protocol[0],protocol_edges)
            
            elif model.is_derived(v_data["key"],nv_container):
                self.run_container_test(graph,n,model,protocol[0],protocol_edges)

            elif model.is_derived(v_data["key"],nv_instrument):
                self.run_instrument_test(graph,n,model,protocol[0],protocol_edges)

        protocol_file = open(filename)
        runlog, _bundle = simulate(protocol_file)
        action = graph.search((prot_id,nv_actions,None))[0][1][0]
        def _run(action):
            a_id,a_data = action
            runlog_element = runlog.pop(0)
            rl_pl = runlog_element["payload"]
            rl_text = rl_pl["text"]            
            self.assertEqual(_get_name(a_data["key"]).split("-")[0].lower(),rl_text.split()[0].lower(),rl_text)
            sa = graph.search((a_id,nv_actions,None))
            if len(sa) > 1:
                self.fail()
            if len(sa) != 1:
                return
            for sa in resolve_action(graph,sa[0][1][0]):
                _run(sa)

        actions = resolve_action(graph,action)
        for index,action in enumerate(actions):
            _run(action)
        protocol_file.close()

class TestConvertNVProtocol(unittest.TestCase):

    def setUp(self):
        None

    def tearDown(self):
        None

    def test_assembly(self):
        filename = os.path.join(test_dir,"protocols","autoprotocol","nor_assembly.protocol.nv")
        with open(filename) as f:
            json_data = json.load(f)
        model = model_convert(model_fn)         
        graph = protocol_convert(model,filename)

        self.assertEqual(len(json_data["nodes"]),len(graph.nodes))
        self.assertEqual(len(json_data["links"]),len(graph.edges))


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

def resolve_action(graph,action):
    first = None
    rest = None
    actions = []
    while rest != RDF.nil:
        res = graph.search((action,None,None))
        first = [c for c in res if c[2] == RDF.first]
        rest = [c for c in res if c[2] == RDF.rest]
        assert(len(first) == 1)
        assert(len(rest) == 1)
        first = first[0][1]
        rest = rest[0][1]
        action = rest[0]
        rest = rest[1]["key"]
        actions.append(first)
    return actions

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
