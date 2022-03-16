import unittest
import os
import sys
import re

from rdflib import BNode,OWL,URIRef,Literal
sys.path.insert(0, os.path.join(".."))
sys.path.insert(0, os.path.join("..",".."))
from visual.handlers.color_producer import ColorPicker
from visual.design import DesignVisual

curr_dir = os.path.dirname(os.path.realpath(__file__))
test_dir = os.path.join(curr_dir,"..","files","design","sbol")
model_fn = os.path.join(curr_dir,"..","..","utility","nv_design.xml")


class TestPresets(unittest.TestCase):
    def setUp(self):
        filename = os.path.join(test_dir,"nor_gate.xml")
        self.visual = DesignVisual(model_fn,filename)

    def tearDown(self):
        None

    def test_hierarchy(self):
        self.visual.set_hierarchy_preset()
        self.visual.build()

class TestLabels(unittest.TestCase):

    def setUp(self):
        filename = os.path.join(test_dir,"0x3B.xml")
        self.visual = DesignVisual(model_fn,filename)

    def tearDown(self):
        None

    class TestNode(unittest.TestCase):
        def setUp(self):
            filename = os.path.join(test_dir,"0x3B.xml")
            self.visual = DesignVisual(model_fn,filename)

        def tearDown(self):
            None

        def test_none(self):
            view = self.visual._builder.view
            labels = self.visual.add_node_no_labels()
            self.assertEqual(len(labels), len(view.nodes))
            for index,(node,data) in enumerate(view.nodes(data=True)):
                self.assertIsNone(labels[index])
            self.visual.set_hierarchy_view()
            self.visual.set_hierarchy_view()
            view = self.visual._builder.view
            labels = self.visual.add_node_no_labels()
            self.assertEqual(len(labels), len(view.nodes))
            for index,(node,data) in enumerate(view.nodes(data=True)):
                self.assertIsNone(labels[index])

        def test_adjacency(self):
            ret_val = self.visual.add_node_adjacency_labels()
            self.assertIsNone(ret_val)
            def _run_test(view):
                labels = self.visual.add_node_adjacency_labels()
                self.assertEqual(len(labels), len(view.nodes))
                for index,(node,data) in enumerate(view.nodes(data=True)):
                    split = labels[index].split(",")
                    actual_in = int(split[0].split(":")[1])
                    actual_out = int(split[1].split(":")[1])
                    expected_in = view._graph.in_edges(node)
                    expected_out = view._graph.out_edges(node)
                    self.assertEqual(actual_in, len(expected_in))
                    self.assertEqual(actual_out, len(expected_out))
            view = self.visual._builder.view
            _run_test(view)
            self.visual.set_hierarchy_view()
            self.visual.set_hierarchy_view()
            view = self.visual._builder.view
            _run_test(view)
                
        def test_name(self):
            ret_val = self.visual.add_node_name_labels()
            self.assertIsNone(ret_val)
            def _run_tests(view):
                labels = self.visual.add_node_name_labels()
                self.assertEqual(len(labels), len(view.nodes))
                for index,(node,data) in enumerate(view.nodes(data=True)):
                    self.assertIn(_get_name(data["key"]),labels[index])
            view = self.visual._builder.view
            _run_tests(view)
            self.visual.set_hierarchy_view()
            self.visual.set_hierarchy_view()
            view = self.visual._builder.view
            _run_tests(view)

        def test_class_type(self):
            ret_val = self.visual.add_node_type_labels()
            self.assertIsNone(ret_val)
            def _run_tests(view):
                labels = self.visual.add_node_type_labels()
                self.assertEqual(len(labels), len(view.nodes))
                for index,(node,data) in enumerate(view.nodes(data=True)):
                    n_type = self.visual._builder.get_rdf_type(node)
                    if n_type is not None:
                        actual_type = labels[index]
                        expected_type = _get_name(n_type[1]["key"])
                        self.assertEqual(expected_type,actual_type)
                    elif isdesign(data["key"],URIRef):
                        self.assertEqual(labels[index], "Identifier")
                    elif isdesign(data["key"],Literal):
                        self.assertEqual(labels[index], "Literal")
                    else:
                        self.assertEqual(labels[index], "?")
            view = self.visual._builder.view
            _run_tests(view)
            self.visual.set_hierarchy_view()
            self.visual.set_hierarchy_view()
            view = self.visual._builder.view
            _run_tests(view)
    



    class TestEdge(unittest.TestCase):

        def setUp(self):
            filename = os.path.join(test_dir,"0x3B.xml")
            self.visual = DesignVisual(model_fn,filename)

        def tearDown(self):
            None

        def test_none(self):
            def _run_tests(view):
                labels = self.visual.add_edge_no_labels()
                self.assertEqual(len(labels), len(view.edges))
                for index,(n,v,k,e) in enumerate(view.edges(keys=True,data=True)):
                    self.assertIsNone(labels[index])
            view = self.visual._builder.view
            _run_tests(view)
            self.visual.set_hierarchy_view()
            self.visual.set_hierarchy_view()
            view = self.visual._builder.view
            _run_tests(view)

        def test_name(self):
            view = self.visual._builder.view
            ret_val = self.visual.add_edge_name_labels()
            self.assertIsNone(ret_val)
            def _run_tests(view):
                labels = self.visual.add_edge_name_labels()
                self.assertEqual(len(labels), len(view.edges))
                for index,(n,v,k,e) in enumerate(view.edges(keys=True,data=True)):
                    self.assertEqual(_get_name(e["display_name"]), labels[index])
            view = self.visual._builder.view
            _run_tests(view)
            self.visual.set_hierarchy_view()
            self.visual.set_hierarchy_view()
            view = self.visual._builder.view
            _run_tests(view)

class TestColor(unittest.TestCase):
    class TestNode(unittest.TestCase):

        def setUp(self):
            filename = os.path.join(test_dir,"nor_gate.xml")
            self.visual = DesignVisual(model_fn,filename)
            self._color_list = ColorPicker()

        def tearDown(self):
            None

        def test_standard(self):
            def run_tests(view):
                colors = self.visual.add_standard_node_color()
                self.assertEqual(len(colors), len(view.nodes))
                for index,(node,data) in enumerate(view.nodes(data=True)):
                    self.assertEqual(colors[index], {"standard" : self._color_list[0]})

            view = self.visual._builder.view
            run_tests(view)
            self.visual.set_hierarchy_view()
            self.visual.set_hierarchy_view()
            view = self.visual._builder.view
            run_tests(view)

        def test_rdf_type(self):
            view = self.visual._builder.view
            ret_val = self.visual.add_rdf_type_node_color()
            self.assertIsNone(ret_val)
            def run_tests(view):
                colors = self.visual.add_rdf_type_node_color()
                self.assertEqual(len(colors), len(view.nodes))
                for index,(node,data) in enumerate(view.nodes(data=True)):
                    if self.visual._builder.get_rdf_type(node) is None:
                        self.assertEqual(colors[index], {"no_type" : self._color_list[1]} )
                    else:
                        self.assertEqual(colors[index], {"rdf_type" :  self._color_list[0]} )
            run_tests(view)
            self.visual.set_hierarchy_view()
            self.visual.set_hierarchy_view()
            view = self.visual._builder.view
            run_tests(view)

        def test_type(self):
            view = self.visual._builder.view
            ret_val = self.visual.add_type_node_color()
            self.assertIsNone(ret_val)
            def run_tests(view):
                colors = self.visual.add_type_node_color()
                col_map = {}
                index = 1

                self.assertEqual(len(colors), len(view.nodes))
                for index,(node,data) in enumerate(view.nodes(data=True)):
                    color = colors[index]
                    rdf_type = self.visual._builder.get_rdf_type(node) 
                    if rdf_type is None:
                        self.assertEqual(color, {"No_Role" : self._color_list[0]} )
                    else:
                        color = colors[index]
                        key = list(color.keys())[0]
                        val = list(color.values())[0]
                        self.assertIn(key,rdf_type[1]["key"])
                        self.assertIn(val,self._color_list)

            run_tests(view)
            self.visual.set_hierarchy_view()
            self.visual.set_hierarchy_view()
            view = self.visual._builder.view
            run_tests(view)

        def test_hierarchy(self):
            view = self.visual._builder.view
            ret_val = self.visual.add_hierarchy_node_color()
            self.assertIsNone(ret_val)
            def _run_tests():
                colors = self.visual.add_hierarchy_node_color()
                c_pass,message = _test_color_map(colors,False)
                self.assertEqual(c_pass,1,message)

                self.assertEqual(len(colors), len(view.nodes))
                all_classes_ids = [c[0] for c in self.visual._builder.get_entities()]
                all_classes = [c[1]["key"] for c in self.visual._builder.get_entities()]
                for index,(node,data) in enumerate(view.nodes(data=True)):
                    if data["key"] not in all_classes:
                        if any(x in [c[0] for c in view.in_edges(node)] for x in all_classes_ids):
                            color = colors[index]
                            key = list(color.keys())[0]
                            val = list(color.values())[0]
                            self.assertIn(val,self._color_list)
                        else:
                            self.assertEqual(colors[index], {"Non-Hierarchical" : self._color_list[0]} )
                    else:
                        color = colors[index]
                        key = list(color.keys())[0]
                        val = list(color.values())[0]
                        self.assertIn(val,self._color_list)
                        actual_depth = self.visual._builder.get_entity_depth(node)
                        expected_depth = int(key.split("-")[-1])
                        self.assertEqual(expected_depth,actual_depth)
            _run_tests()
            self.visual.set_hierarchy_view()
            self.visual.set_hierarchy_view()
            view = self.visual._builder.view
            _run_tests()

        def test_role(self):
            view = self.visual._builder.view
            ret_val = self.visual.add_role_node_color()
            self.assertIsNone(ret_val)
            def run_tests(view):
                colors = self.visual.add_role_node_color()
                col_map = {}
                index = 1

                self.assertEqual(len(colors), len(view.nodes))
                for index,(node,data) in enumerate(view.nodes(data=True)):
                    color = colors[index]
                    rdf_type = self.visual._builder.get_rdf_type(node) 
                    if rdf_type is None:
                        self.assertEqual(color, {"No_Role" : self._color_list[0]} )
                    else:
                        color = colors[index]
                        key = list(color.keys())[0]
                        val = list(color.values())[0]
                        self.assertIn(key,rdf_type[1]["key"])
                        self.assertIn(val,self._color_list)

            run_tests(view)
            self.visual.set_hierarchy_view()
            self.visual.set_hierarchy_view()
            view = self.visual._builder.view
            run_tests(view)
        
    class TestEdge(unittest.TestCase):

        def setUp(self):
            filename = os.path.join(test_dir,"0x3B.xml")
            self.visual = DesignVisual(model_fn,filename)
            self._color_list = ColorPicker()

        def tearDown(self):
            None

        def test_standard(self):
            view = self.visual._builder.view
            colors = self.visual.add_standard_edge_color()
            self.assertEqual(len(colors), len(view.edges))
            for index,(n,v,e) in enumerate(view.edges(data=True)):
                self.assertEqual(colors[index], {"standard" : "#888"} )

            self.visual.set_hierarchy_view()
            self.visual.set_hierarchy_view()

            view = self.visual._builder.view
            colors = self.visual.add_standard_edge_color()
            self.assertEqual(len(colors), len(view.edges))
            for index,(n,v,e) in enumerate(view.edges(data=True)):
                self.assertEqual(colors[index], {"standard" : "#888"})

        def test_hierarchy(self):
            view = self.visual._builder.view
            ret_val = self.visual.add_hierarchy_edge_color()
            self.assertIsNone(ret_val)
            
            view = self.visual._builder.view
            def _run_tests():
                colors = self.visual.add_hierarchy_edge_color()
                self.assertEqual(len(colors), len(view.edges))
                all_classes_ids = [c[0] for c in self.visual._builder.get_entities()]
                all_classes = [c[1]["key"] for c in self.visual._builder.get_entities()]
                c_pass,message = _test_color_map(colors,False)
                self.assertEqual(c_pass,1,message)

                for index,(n,v,k) in enumerate(view.edges(keys=True)):
                    n_data = view.nodes[n]
                    if n_data["key"] not in all_classes:
                        if any(x in [c[0] for c in view.in_edges(n)] for x in all_classes_ids):
                            color = colors[index]
                            key = list(color.keys())[0]
                            val = list(color.values())[0]
                            self.assertIn(val,self._color_list)
                        else:
                            self.assertEqual(colors[index], {"Non-Hierarchical" : self._color_list[0]} )
                    else:
                        color = colors[index]
                        key = list(color.keys())[0]
                        val = list(color.values())[0]
                        self.assertIn(val,self._color_list)
                        actual_depth = self.visual._builder.get_entity_depth(n)
                        expected_depth = int(key.split("-")[-1])
                        self.assertEqual(expected_depth,actual_depth)
            _run_tests()
            self.visual.set_hierarchy_view()
            self.visual.set_hierarchy_view()
            view = self.visual._builder.view
            _run_tests()
            
class TestShape(unittest.TestCase):
    def setUp(self):
        filename = os.path.join(test_dir,"0x3B.xml")
        self.visual = DesignVisual(model_fn,filename)

    def tearDown(self):
        None
    
    def test_adaptive(self):
        view = self.visual._builder.view
        ret_val = self.visual.set_adaptive_node_shape()
        self.assertIsNone(ret_val)
        def _run_tests():    
            shapes = self.visual.set_adaptive_node_shape()
            s_list = self.visual._shape_h.node.shapes
            default_shape = s_list[0]
            shapes_l = s_list[1:]
            counter = 0
            shape_map = {"no_type" : default_shape}
            shapes = self.visual.set_adaptive_node_shape()
            self.assertEqual(len(shapes), len(view.nodes))
            for index,(node,data) in enumerate(view.nodes(data=True)):
                n_type = self.visual._builder.get_rdf_type(node)
                if n_type is None:
                    expected_shape = {"No Type" : shape_map["no_type"]}
                else:
                    n_type = n_type[1]["key"]
                    if n_type not in shape_map.keys():
                        shape_map[n_type] = shapes_l[counter]
                        if counter == len(shapes_l) - 1:
                            counter = 0
                        else:
                            counter = counter + 1 
                    expected_shape = {_get_name(n_type) : shape_map[n_type]}
                self.assertEqual(shapes[index], expected_shape)

        _run_tests()
        self.visual.set_hierarchy_view()
        self.visual.set_hierarchy_view()
        view = self.visual._builder.view
        _run_tests()

class TestSize(unittest.TestCase):
    def setUp(self):
        filename = os.path.join(test_dir,"0x3B.xml")
        self.visual = DesignVisual(model_fn,filename)
        self.builder = self.visual._builder
        self.standard_node_size = self.visual._size_h._standard_node_size
        self.max_node_size = self.visual._size_h._max_node_size
        self.modifier = self.visual._size_h._modifier

    def tearDown(self):
        None

    def test_standard(self):
        view = self.visual._builder.view
        sizes = self.visual.add_standard_node_size()
        self.assertEqual(len(sizes), len(view.nodes))
        for index,(node,data) in enumerate(view.nodes(data=True)):
            self.assertEqual(sizes[index], self.standard_node_size)

        self.visual.set_hierarchy_view()
        self.visual.set_hierarchy_view()

        view = self.visual._builder.view
        sizes = self.visual.add_standard_node_size()
        self.assertEqual(len(sizes), len(view.nodes))
        for index,(node,data) in enumerate(view.nodes(data=True)):
            self.assertEqual(sizes[index], self.standard_node_size)

    def test_rdf_type(self):
        ret = self.visual.add_rdf_type_node_size()
        self.assertIsNone(ret)
        def _run_tests(view,sizes):  
            self.assertEqual(len(sizes),len(view.nodes()))  
            for index,(node,data) in enumerate(view.nodes(data=True)):
                node_size = node_sizes[index]
                if self.builder.get_rdf_type(node) is None:
                    self.assertEqual(node_size,self.standard_node_size/2)
                else:
                    self.assertEqual(node_size,self.standard_node_size)
                    
        node_sizes = self.visual.add_rdf_type_node_size()
        view = self.visual._builder.view
        _run_tests(view,node_sizes)
        self.visual.set_hierarchy_view()
        self.visual.set_hierarchy_view()
        node_sizes = self.visual.add_rdf_type_node_size()
        view = self.visual._builder.view
        _run_tests(view,node_sizes)

    def _centrality_test(self,_cen_func,reduction,expected_node_func):
        ret = _cen_func()
        self.assertIsNone(ret)
        def _run_tests(view,sizes):  
            self.assertEqual(len(sizes),len(view.nodes()))  
            for index,(node,data) in enumerate(view.nodes(data=True)):
                expected_node_size = expected_node_func(view,node)
                expected_node_size = int((expected_node_size * self.standard_node_size) / reduction)
                if expected_node_size > 100:
                    expected_node_size = 100
                if expected_node_size < self.standard_node_size/2:
                    expected_node_size = self.standard_node_size
            self.assertEqual(expected_node_size, sizes[index])

        node_sizes = _cen_func()
        view = self.visual._builder.view
        _run_tests(view,node_sizes)
        self.visual.set_hierarchy_view()
        self.visual.set_hierarchy_view()
        node_sizes = _cen_func()
        view = self.visual._builder.view
        _run_tests(view,node_sizes)

    def test_centrality(self):
        cen_func = self.visual.add_centrality_node_size
        reduction = 4
        def _expected_node_size(view,node):
            return  1 + len(view.in_edges(node)) + len(view.out_edges(node))
        self._centrality_test(cen_func,reduction,_expected_node_size)

    def test_in_centrality(self):
        cen_func = self.visual.add_in_centrality_node_size
        reduction = 2
        def _expected_node_size(view,node):
            return  1 + len(view.in_edges(node))
        self._centrality_test(cen_func,reduction,_expected_node_size)

    def test_out_centrality(self):
        cen_func = self.visual.add_out_centrality_node_size
        reduction = 2
        def _expected_node_size(view,node):
            return  1 + len(view.out_edges(node))
        self._centrality_test(cen_func,reduction,_expected_node_size)
    
    def test_hierarchy(self):
        ret = self.visual.add_hierarchy_node_size()
        self.assertIsNone(ret)

        def _run_tests(view,sizes):  
            self.assertEqual(len(sizes),len(view.nodes()))  
            for index,(node,data) in enumerate(view.nodes(data=True)):
                node_size = node_sizes[index]
                key = data["key"]
                if self.builder.get_rdf_type(node) is None:
                    pass
                else:
                    depth = self.builder.get_entity_depth(node)
                    if depth == 0:
                        self.assertEqual(node_size,self.max_node_size)
                    else:
                        self.assertEqual(node_size,int(self.max_node_size/ (depth * self.modifier)))

        node_sizes = self.visual.add_hierarchy_node_size()
        view = self.visual._builder.view
        _run_tests(view,node_sizes)
        self.visual.set_hierarchy_view()
        self.visual.set_hierarchy_view()
        node_sizes = self.visual.add_hierarchy_node_size()
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
