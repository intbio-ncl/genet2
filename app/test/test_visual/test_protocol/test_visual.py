import unittest
import os
import sys
import re

sys.path.insert(0, os.path.join(".."))
sys.path.insert(0, os.path.join("..",".."))
from visual.handlers.color_producer import ColorPicker
from visual.protocol import ProtocolVisual

curr_dir = os.path.dirname(os.path.realpath(__file__))
test_dir = os.path.join(curr_dir,"..","files")
protocols_dir = os.path.join(test_dir,"protocols","autoprotocol")
model_fn = os.path.join(curr_dir,"..","..","utility","nv_protocol.xml")

class TestLabels(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        None

    class TestNode(unittest.TestCase):
        def setUp(self):
            filename = os.path.join(protocols_dir,"assembly.protocol.nv")
            self.visual = ProtocolVisual(model_fn,filename)

        def tearDown(self):
            None

        def test_parent(self):
            ret_val = self.visual.add_parent_node_labels()
            self.assertIsNone(ret_val)
            def _run_test(view):
                labels = self.visual.add_parent_node_labels()
                self.assertEqual(len(labels), len(view.nodes))
            view = self.visual._builder.view
            _run_test(view)
            self.visual.set_action_flow_view()
            self.visual.set_action_flow_view()
            view = self.visual._builder.view
            _run_test(view)

        def test_well_container(self):
            nv_well = self.visual._builder._model_graph.identifiers.objects.well
            ret_val = self.visual.add_well_container_node_labels()
            self.assertIsNone(ret_val)
            def _run_tests(view):
                labels = self.visual.add_well_container_node_labels()
                self.assertEqual(len(labels), len(view.nodes))
                for index,(n,n_data) in enumerate(view.nodes(data=True)):
                    rdf_type = self.visual._builder.get_rdf_type(n)
                    if rdf_type is not None and rdf_type[1]["key"] == nv_well:
                        parent = self.visual._builder.get_parent(n)
                        self.assertEqual(f'{parent[1]["display_name"]} - {n_data["display_name"]}',labels[index])
                    else:
                        self.assertEqual(n_data["display_name"],labels[index])
            view = self.visual._builder.view
            _run_tests(view)
            self.visual.set_hierarchy_view()
            self.visual.set_hierarchy_view()
            self.visual.set_tree_mode()
            self.visual.set_tree_mode()
            view = self.visual._builder.view
            _run_tests(view)

    class TestEdge(unittest.TestCase):

        def setUp(self):
            filename = os.path.join(protocols_dir,"nor_full.protocol.nv")
            self.visual = ProtocolVisual(model_fn,filename)

        def tearDown(self):
            None

        def test_well_container(self):
            nv_well = self.visual._builder._model_graph.identifiers.objects.well
            ret_val = self.visual.add_well_container_edge_labels()
            self.assertIsNone(ret_val)
            def _run_tests(view):
                labels = self.visual.add_well_container_edge_labels()
                self.assertEqual(len(labels), len(view.nodes))
                for index,(n,n_data) in enumerate(view.nodes(data=True)):
                    rdf_type = self.visual._builder.get_rdf_type(n)
                    if rdf_type is not None and rdf_type[1]["key"] == nv_well:
                        parent = self.visual._builder.get_parent(n)
                        self.assertEqual(f'{parent[1]["display_name"]} - {n_data["display_name"]}',labels[index])
                    else:
                        self.assertEqual(n_data["display_name"],labels[index])
            view = self.visual._builder.view
            _run_tests(view)
            self.visual.set_hierarchy_view()
            self.visual.set_hierarchy_view()
            self.visual.set_tree_mode()
            self.visual.set_tree_mode()
            view = self.visual._builder.view
            _run_tests(view)

class TestColor(unittest.TestCase):
    
    class TestNode(unittest.TestCase):

        def setUp(self):
            filename = os.path.join(test_dir,"assembly.protocol.nv")
            self.visual = ProtocolVisual(model_fn,filename)

            self._color_list = ColorPicker()

        def tearDown(self):
            None

        def test_parent(self):
            ret_val = self.visual.add_parent_node_color()
            self.assertIsNone(ret_val)
            def _run_test(view):
                labels = self.visual.add_parent_node_color()
                self.assertEqual(len(labels), len(view.nodes))
            view = self.visual._builder.view
            _run_test(view)
            self.visual.set_action_flow_view()
            self.visual.set_action_flow_view()
            view = self.visual._builder.view
            _run_test(view)
        
    class TestEdge(unittest.TestCase):
        def setUp(self):
            filename = os.path.join(test_dir,"1_clip.ot2.py")
            self.visual = ProtocolVisual(model_fn,filename)
            self._color_list = ColorPicker()

        def tearDown(self):
            None

        def test_object_type(self):
            ret_val = self.visual.add_object_type_edge_color()
            self.assertIsNone(ret_val)
            def _run_test(view):
                labels = self.visual.add_object_type_edge_color()
                #self.assertEqual(len(labels), len(view.nodes))
            view = self.visual._builder.view
            _run_test(view)
            self.visual.set_action_io_implicit_view()
            self.visual.set_action_io_implicit_view()
            view = self.visual._builder.view
            _run_test(view)
            
class TestShape(unittest.TestCase):
    def setUp(self):
        filename = os.path.join(test_dir,"0x3B.xml")
        self.visual = ProtocolVisual(model_fn,filename)

    def tearDown(self):
        None

class TestSize(unittest.TestCase):
    def setUp(self):
        filename = os.path.join(test_dir,"protocols","opentrons","1_clip.ot2.py")
        self.visual = ProtocolVisual(model_fn,filename)
        self.standard_node_size = self.visual._size_h._standard_node_size
        self.max_node_size = self.visual._size_h._max_node_size
        self.modifier = self.visual._size_h._modifier

    def tearDown(self):
        None

    def test_action(self):
        ret = self.visual.add_action_node_size()
        self.assertIsNone(ret)
        def _run_tests(view,sizes):  
            self.assertEqual(len(sizes),len(view.nodes()))  
            for index,(node,data) in enumerate(view.nodes(data=True)):
                node_size = node_sizes[index]
                    
        node_sizes = self.visual.add_action_node_size()
        view = self.visual._builder.view
        _run_tests(view,node_sizes)
        self.visual.set_io_view()
        self.visual.set_io_view()
        node_sizes = self.visual.add_action_node_size()
        view = self.visual._builder.view
        _run_tests(view,node_sizes)

def _test_color_map(colors,unique_keys=True):
    for color in colors:
        key = list(color.keys())[0]
        val = list(color.values())[0]
        for c in colors:
            try:
                if c[key] != val:
                    return -1,f'{c[key]} != {val}'
            except KeyError:
                if unique_keys and list(c.values())[0] == val:
                    return -1, f'{list(c.values())[0]} == {val}'
        return 1,""

def _get_name(subject):
    split_subject = _split(subject)
    if len(split_subject[-1]) == 1 and split_subject[-1].isdigit():
        return split_subject[-2]
    elif len(split_subject[-1]) == 3 and _isfloat(split_subject[-1]):
        return split_subject[-2]
    else:
        return split_subject[-1]

def _split(uri):
    return re.split('#|\/|:', uri)

def _isfloat(x):
    try:
        float(x)
        return True
    except ValueError:
        return False


if __name__ == '__main__':
    unittest.main()
