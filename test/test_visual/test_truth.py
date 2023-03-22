import unittest
import os
import sys
import re

sys.path.insert(0, os.path.join(".."))
sys.path.insert(0, os.path.join("..",".."))
sys.path.insert(0, os.path.join("..","..",".."))

from app.visualiser.visual.handlers.color_producer import ColorPicker
from app.visualiser.visual.truth import TruthVisual
from app.graph.world_graph import WorldGraph

curr_dir = os.path.dirname(os.path.realpath(__file__))
test_fn = os.path.join(curr_dir,"..","files","nor_full.xml")

class TestColor(unittest.TestCase):
    class TestEdge(unittest.TestCase):

        @classmethod
        def setUpClass(self):
            self._wrapper = WorldGraph()
            self.visual = TruthVisual(self._wrapper)
            self.visual.set_full_graph_view()
            self._color_list = ColorPicker()
            self.visual._builder.build()

        @classmethod
        def tearDownClass(self):
            pass

        def test_confidence(self):
            view = self.visual._builder.view
            ret_val =             self.visual.add_confidence_edge_color()
            self.assertIsNone(ret_val)
            view = self.visual._builder.view
            def _run_tests():
                mapper = {}
                colors = self.visual.add_confidence_edge_color()
                edges = [*view.edges()]
                self.assertEqual(len(colors), len(edges))
                for index,edge in enumerate(edges):
                    color = colors[index]
                    labs = edge.get_type()
                    if labs in mapper:
                        self.assertEqual(color,mapper[labs])
                    else:
                        mapper[labs] = color
                    
            _run_tests()
            self.visual.set_hierarchy_view()
            self.visual.set_hierarchy_view()
            view = self.visual._builder.view
            _run_tests()
       
if __name__ == '__main__':
    unittest.main()
