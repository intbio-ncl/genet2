import os
import json
import dash_cytoscape as cyto
cyto.load_extra_layouts()

default_stylesheet_fn = os.path.join(os.path.dirname(
    os.path.realpath(__file__)), "default_stylesheet.txt")

class AbstractVisual:
    def __init__(self):
        self.view = self.set_full_graph_view
        self.mode = self.set_network_mode
        self.node_text = self.add_node_no_labels
        self.edge_text = self.add_edge_no_labels
        self.node_color = self.add_standard_node_color
        self.edge_color = self.add_standard_edge_color
        self.node_size = self.add_standard_node_size
        self.node_shape = self.set_circle_node_shape
        self.edge_shape = self.set_straight_edge_shape
        self.stylesheet = []

    def copy_settings(self):
        current_settings = [
            self.layout,
            self.node_text,
            self.edge_text,
            self.node_color,
            self.edge_color,
            self.node_size,
            self.node_shape]
        return current_settings

    # ---------------------- View ------------------------------------
    def set_full_graph_view(self):
        '''
        Renders the Full graph. 
        '''
        if self.view == self.set_full_graph_view:
            self._builder.set_full_view()
        else:
            self.view = self.set_full_graph_view

    # ---------------------- View Mode ------------------------------------
    def set_network_mode(self):
        '''
        Set the graph to the standard Node-Edge-Node Network graph.
        '''
        if self.mode == self.set_network_mode:
            self._builder.set_network_mode()
        else:
            self.mode = self.set_network_mode

    def set_tree_mode(self):
        '''
        Produce a Tree-Like graph where duplicates within 
        the graph are NOT treated as the same node.
        This will result in a tree/heirarchy structure within a graph.
        '''
        if self.mode == self.set_tree_mode:
            self._builder.set_tree_mode()
        else:
            self.mode = self.set_tree_mode

    def set_union_mode(self):
        '''
        Only for multiple graph visualisation. 
        Connects graphs by merging duplicate nodes between graphs.
        '''
        if self.mode == self.set_union_mode:
            self._builder.set_union_mode()
        else:
            self.mode = self.set_union_mode


    def set_node_difference_mode(self):
        '''
        Only for multiple graph visualisation. 
        Visualised the difference between Graphs. 
        I.e. where common nodes are removed. 
        Differs from edge_different as graph will become connected i.e. common nodes are 
        merged and edges between rest are linked to unique nodes.
        '''
        if self.mode == self.set_node_difference_mode:
            self._builder.set_node_difference_mode()
        else:
            self.mode = self.set_node_difference_mode


    def set_edge_difference_mode(self):
        '''
        Only for multiple graph visualisation. 
        Visualised the difference between Graphs. 
        I.e. where common nodes and edges are removed. 
        Differs from node_difference as graphs will still be 
        disconnected and only edges will be removed that are common.
        '''
        if self.mode == self.set_edge_difference_mode:
            self._builder.set_edge_difference_mode()
        else:
            self.mode = self.set_edge_difference_mode


    def set_node_intersection_mode(self):
        '''
        Only for multiple graph visualisation. 
        Visualised the intersection between Graphs. 
        I.e. where non common nodes are removed. 
        Result is a merged graph with all edges of 
        common nodes attached.
        '''
        if self.mode == self.set_node_intersection_mode:
            self._builder.set_node_intersection_mode()
        else:
            self.mode = self.set_node_intersection_mode


    def set_edge_intersection_mode(self):
        '''
        Only for multiple graph visualisation. 
        Visualised the intersection between Graphs. 
        I.e. where only common edges are maintained.
        Similar to node intersection but takes edge between nodes into 
        account opposed to each node individually.
        '''
        if self.mode == self.set_edge_intersection_mode:
            self._builder.set_edge_intersection_mode()
        else:
            self.mode = self.set_edge_intersection_mode

# ---------------------- Pick a layout ----------------------
    def _set_layout(self, obj):
        if not hasattr(self, 'layout') or not isinstance(self.layout, obj):
            self.layout = obj()

    def set_no_layout(self):
        '''
        No new positional data produced for graph.
        '''
        self._set_layout(self._layout_h.No)

    def set_concentric_layout(self):
        '''
        Position nodes into concentric circles, 
        based on the specified metric. 
        '''
        self._set_layout(self._layout_h.Concentric)

    def set_breadthfirst_layout(self):
        '''
        Positions nodes in levels, according to the levels 
        generated by running a breadth-first search on the graph.
        '''
        self._set_layout(self._layout_h.BreadthFirst)

    def set_cose_layout(self):
        '''
        Positions nodes based on the CoSE: Compound Spring Embedder - 
        A force directed layout scheme.
        '''
        self._set_layout(self._layout_h.Cose)

    def set_cose_bilkent_layout(self):
        '''
        Positions nodes based on the CoSE: Compound Spring Embedder - 
        A force directed layout scheme.
        Similar to COSE but more expensive + can provide better results.
        '''
        self._set_layout(self._layout_h.CoseBilkent)

    def set_cola_layout(self):
        '''
        Positions nodes based on a force directed algorithm.
        '''
        self._set_layout(self._layout_h.Cola)

    def set_euler_layout(self):
        '''
        Positions nodes based on a force directed algorithm.
        It is fairly fast. However, cola tends to give better results.
        '''
        self._set_layout(self._layout_h.Euler)

    def set_spread_layout(self):
        '''
        Positions nodes based on a force directed algorithm.
        First, it runs cose and then it spreads out the graph 
        to fill out the viewport as much as possible.
        '''
        self._set_layout(self._layout_h.Spread)

    def set_dagre_layout(self):
        '''
        Positions nodes based on a traditional binary 
        tree heirarchical layout.
        '''
        self._set_layout(self._layout_h.Dagre)

    def set_klay_layout(self):
        '''
        Positions nodes based on a heirarchical layout.
        '''
        self._set_layout(self._layout_h.Klay)

    def set_grid_layout(self):
        '''
        Positions nodes based on a heirarchical layout.
        '''
        self._set_layout(self._layout_h.Grid)

    def set_circle_layout(self):
        '''
        Positions nodes based on a circular layout.
        '''
        self._set_layout(self._layout_h.Circle)

    def set_spread_layout(self):
        '''
        Positions nodes by increasing max distance.
        '''
        self._set_layout(self._layout_h.Spread)

    def set_random_layout(self):
        '''
        Positions nodes by random.
        '''
        self._set_layout(self._layout_h.Random)

    # ---------------------- Node Labels ----------------------

    def add_node_no_labels(self):
        '''
        Textual data pertaining to a node is not rendered.
        '''
        if self.node_text == self.add_node_no_labels:
            return self._label_h.node.none()
        else:
            self.node_text = self.add_node_no_labels

    def add_node_adjacency_labels(self):
        '''
        Textual data pertaining to a node relates 
        to number of incoming and outgoing edges.
        '''
        if self.node_text == self.add_node_adjacency_labels:
            return self._label_h.node.adjacency()
        else:
            self.node_text = self.add_node_adjacency_labels

    def add_node_name_labels(self):
        '''
        Textual data pertaining to a node relates to the 
        name the node was provided during building of the graph.
        '''
        if self.node_text == self.add_node_name_labels:
            return self._label_h.node.name()
        else:
            self.node_text = self.add_node_name_labels

    def add_node_type_labels(self):
        '''
        Textual data pertaining to a node is of the RDF type.
        '''
        if self.node_text == self.add_node_type_labels:
            return self._label_h.node.class_type()
        else:
            self.node_text = self.add_node_type_labels
    
    def add_node_uri_labels(self):
        '''
        Textual data pertaining to a nodes URI if possible else name.
        '''
        if self.node_text == self.add_node_uri_labels:
            return self._label_h.node.uri()
        else:
            self.node_text = self.add_node_uri_labels


    # ---------------------- Edge Labels ----------------------
    def add_edge_no_labels(self):
        '''
        Textual data pertaining to a egde is not rendered.
        '''
        if self.edge_text == self.add_edge_no_labels:
            return self._label_h.edge.none()
        else:
            self.edge_text = self.add_edge_no_labels

    def add_edge_name_labels(self):
        '''
        Textual data pertaining relates to the 
        name provides when building the graph.
        '''
        if self.edge_text == self.add_edge_name_labels:
            return self._label_h.edge.name()
        else:
            self.edge_text = self.add_edge_name_labels

    def add_edge_uri_labels(self):
        '''
        Textual data pertaining to a edges URI if possible else name.
        '''
        if self.edge_text == self.add_edge_uri_labels:
            return self._label_h.edge.uri()
        else:
            self.edge_text = self.add_edge_uri_labels

    # ---------------------- Node Color ----------------------
    def add_standard_node_color(self):
        '''
        All node colors are the same standard color.
        '''
        if self.node_color == self.add_standard_node_color:
            return self._color_h.node.standard()
        else:
            self.node_color = self.add_standard_node_color

    def add_rdf_type_node_color(self):
        '''
        Di-color, Objects and Properties have a unique color.
        '''
        if self.node_color == self.add_rdf_type_node_color:
            return self._color_h.node.rdf_type()
        else:
            self.node_color = self.add_rdf_type_node_color

    def set_graph_name_node_color(self):
        '''
        All node colors pertain to the name 
        of the source graph when loaded.
        '''
        if self.node_color == self.set_graph_name_node_color:
            return self._color_h.node.graph_name()
        else:
            self.node_color = self.set_graph_name_node_color
    # ---------------------- Edge Color ----------------------

    def add_standard_edge_color(self):
        '''
        The color pertaining to each edge is uniform. 
        '''
        if self.edge_color == self.add_standard_edge_color:
            return self._color_h.edge.standard()
        else:
            self.edge_color = self.add_standard_edge_color

    def add_type_edge_color(self):
        '''
        All edge types are mapped to distinct color.
        '''
        if self.edge_color == self.add_type_edge_color:
            return self._color_h.edge.nv_type()
        else:
            self.edge_color = self.add_type_edge_color

    def set_graph_name_edge_color(self):
        '''
        All edge colors pertain to the name 
        of the source graph when loaded.
        '''
        if self.edge_color == self.set_graph_name_edge_color:
            return self._color_h.edge.graph_name()
        else:
            self.edge_color = self.set_graph_name_edge_color

    # ---------------------- Node Size ----------------------
    def add_standard_node_size(self):
        '''
        The Node size for each node is equal.
        '''
        if self.node_size == self.add_standard_node_size:
            return self._size_h.standard()
        else:
            self.node_size = self.add_standard_node_size

    def add_rdf_type_node_size(self):
        '''
        The Node size for each node is based on whether it is 
        a Object or a property i.e. does the node has an RDF type.
        '''
        if self.node_size == self.add_rdf_type_node_size:
            return self._size_h.class_type()
        else:
            self.node_size = self.add_rdf_type_node_size

    def add_centrality_node_size(self):
        '''
        The Node size is greater the more 
        incoming + outgoing edges of said node. 
        '''
        if self.node_size == self.add_centrality_node_size:
            return self._size_h.centrality()
        else:
            self.node_size = self.add_centrality_node_size

    def add_in_centrality_node_size(self):
        '''
        The Node size is greater the more 
        incoming edges of said node. 
        '''
        if self.node_size == self.add_in_centrality_node_size:
            return self._size_h.in_centrality()
        else:
            self.node_size = self.add_in_centrality_node_size

    def add_out_centrality_node_size(self):
        '''
        The Node size is greater the more 
        outgoing edges of said node. 
        '''
        if self.node_size == self.add_out_centrality_node_size:
            return self._size_h.out_centrality()
        else:
            self.node_size = self.add_out_centrality_node_size

    # ---------------------- Node Shape ----------------------
    def set_adaptive_node_shape(self):
        '''
        Sets the shape of each node based on the RDF type of given node.
        '''
        if self.node_shape == self.set_adaptive_node_shape:
            return self._shape_h.node.adaptive()
        else:
            self.node_shape = self.set_adaptive_node_shape

    def set_circle_node_shape(self):
        '''
        Sets the shape of each node to a circle.
        '''
        if self.node_shape == self.set_circle_node_shape:
            return self._shape_h.node.circle()
        else:
            self.node_shape = self.set_circle_node_shape

    def set_square_node_shape(self):
        '''
        Sets the shape of each node to a square.
        '''
        if self.node_shape == self.set_square_node_shape:
            return self._shape_h.node.square()
        else:
            self.node_shape = self.set_square_node_shape

    def set_triangle_node_shape(self):
        '''
        Sets the shape of each node to a triangle.
        '''
        if self.node_shape == self.set_triangle_node_shape:
            return self._shape_h.node.triangle()
        else:
            self.node_shape = self.set_triangle_node_shape

    def set_rectangle_node_shape(self):
        '''
        Sets the shape of each node to a rectangle.
        '''
        if self.node_shape == self.set_rectangle_node_shape:
            return self._shape_h.node.rectangle()
        else:
            self.node_shape = self.set_rectangle_node_shape

    def set_diamond_node_shape(self):
        '''
        Sets the shape of each node to a diamond.
        '''
        if self.node_shape == self.set_diamond_node_shape:
            return self._shape_h.node.diamond()
        else:
            self.node_shape = self.set_diamond_node_shape

    def set_hexagon_node_shape(self):
        '''
        Sets the shape of each node to a hexagon.
        '''
        if self.node_shape == self.set_hexagon_node_shape:
            return self._shape_h.node.hexagon()
        else:
            self.node_shape = self.set_hexagon_node_shape

    def set_octagon_node_shape(self):
        '''
        Sets the shape of each node to a octagon.
        '''
        if self.node_shape == self.set_octagon_node_shape:
            return self._shape_h.node.octagon()
        else:
            self.node_shape = self.set_octagon_node_shape

    def set_vee_node_shape(self):
        '''
        Sets the shape of each node to a vee.
        '''
        if self.node_shape == self.set_vee_node_shape:
            return self._shape_h.node.vee()
        else:
            self.node_shape = self.set_vee_node_shape

    # ---------------------- Edge Shape ----------------------
    def set_straight_edge_shape(self):
        '''
        Sets the shape of each edge to a straight line.
        '''
        if self.edge_shape == self.set_straight_edge_shape:
            return self._shape_h.edge.straight()
        else:
            self.edge_shape = self.set_straight_edge_shape

    def set_bezier_edge_shape(self):
        '''
        Sets the shape of each edge to a straight line.
        Overlapping edges are curved.
        '''
        if self.edge_shape == self.set_bezier_edge_shape:
            return self._shape_h.edge.bezier()
        else:
            self.edge_shape = self.set_bezier_edge_shape

    def set_taxi_edge_shape(self):
        '''
        Sets the shape of each edge to a two straight 
        lines with a right angle.
        '''
        if self.edge_shape == self.set_taxi_edge_shape:
            return self._shape_h.edge.taxi()
        else:
            self.edge_shape = self.set_taxi_edge_shape

    def set_unbundled_bezier_edge_shape(self):
        '''
        Sets the shape of each edge based on the unbundled_bezier algorithm.
        '''
        if self.edge_shape == self.set_unbundled_bezier_edge_shape:
            return self._shape_h.edge.unbundled_bezier()
        else:
            self.edge_shape = self.set_unbundled_bezier_edge_shape

    def set_loop_edge_shape(self):
        '''
        Sets the shape of each edge to a loop .
        '''
        if self.edge_shape == self.set_loop_edge_shape:
            return self._shape_h.edge.loop()
        else:
            self.edge_shape = self.set_loop_edge_shape

    def set_haystack_edge_shape(self):
        '''
        Sets the shape of each edge based on the haystack algorithm.
        '''
        if self.edge_shape == self.set_haystack_edge_shape:
            return self._shape_h.edge.haystack()
        else:
            self.edge_shape = self.set_haystack_edge_shape

    def set_segments_edge_shape(self):
        '''
        Sets the shape of each edge to a set of segments. 
        '''
        if self.edge_shape == self.set_segments_edge_shape:
            return self._shape_h.edge.segments()
        else:
            self.edge_shape = self.set_segments_edge_shape

    def empty_graph(self,graph_id):
        return cyto.Cytoscape(id=graph_id,layout=self.layout.build(),elements = [])

    def build(self, graph_id="cytoscape_graph", legend=False,datatable=False, width=80, height=100):
        rets = []
        stylesheet = self._build_default_stylesheet()
        nodes = []
        edges = []
        node_selectors = []
        edge_selectors = []
        self.view()
        if datatable:
            dt = self._builder.build(True)
        else:
            self._builder.build()
        self.mode()
        
        node_color = self.node_color()
        node_shapes = self.node_shape()
        node_sizes = self.node_size()
        edge_color = self.edge_color()
        node_text = self.node_text()
        edge_text = self.edge_text()
        edge_shape = self.edge_shape()

        if self.layout is not None:
            layout = self.layout.build()
        for index, node in enumerate(self._builder.view.nodes()):
            text = node_text[index]
            color_key = list(node_color[index].keys())[0]
            shape = node_shapes[index]
            shape = str(list(shape.values())[0])
            size = node_sizes[index]
            n_color = node_color[index][color_key]
            node, n_style = self._build_node(
                node, text, size, color_key, n_color, shape)
            if color_key not in node_selectors:
                stylesheet.append(n_style)
                node_selectors.append(color_key)
            nodes.append(node)

        for index, edge in enumerate(self._builder.view.edges()):
            color_key = list(edge_color[index].keys())[0]
            e_color = edge_color[index][color_key]
            edge, e_style = self._build_edge(edge, edge_text[index], color_key, e_color, edge_shape)
            if color_key not in edge_selectors:
                stylesheet.append(e_style)
                edge_selectors.append(color_key)
            edges.append(edge)
        figure = cyto.Cytoscape(id=graph_id,
                                layout=layout,
                                style={
                                    'width': f'{str(width)}vw', 'height': f'{str(height)}vh'},
                                elements=nodes + edges,
                                stylesheet=stylesheet,
                                responsive=True)
        rets.append(figure)
        self.stylesheet = stylesheet
        if legend:
            legend_dict = self._build_legend(node_color, edge_color)
            rets.append(legend_dict)
        if datatable:
            rets.append(dt)
        return rets

    def _build_node(self, n, label, size, c_key, color, shape):
        class_str = f'top-center {c_key} {shape}'
        node = {'data': {'id': n.id, 'label': label, "size": size},
                'classes': class_str}
        style = {"selector": "." + c_key, "style": {"background-color": color}}
        return node, style

    def _build_edge(self, edge, label, c_key, color, edge_shape):
        edge = {'data': {'source': edge.n.id, 'target': edge.v.id, 'label': label},
                'classes': f'center-right {c_key}'}
        style = {"selector": "." + c_key, "style": {"line-color": color,
                                                    'curve-style': edge_shape,
                                                    "mid-target-arrow-color": color,
                                                    "mid-target-arrow-shape": "triangle"}}
        return edge, style

    def _build_legend(self, node_colors=[], edge_colors=[], node_shapes=[], node_sizes=[]):
        legend_dict = {}
        f_node_colors = {}
        f_edge_colors = {}
        f_node_shapes = {}
        f_node_sizes = {}
        for node_color in node_colors:
            for k, v in node_color.items():
                f_node_colors[k] = v
        if len(f_node_colors) > 0:
            legend_dict["Node Color"] = f_node_colors
        for edge_color in edge_colors:
            for k, v in edge_color.items():
                f_edge_colors[k] = v
        if len(f_edge_colors) > 0:
            legend_dict["Edge Color"] = f_edge_colors
        for node_shape in node_shapes:
            for k, v in node_shape.items():
                f_node_shapes[k] = v
        if len(f_node_shapes) > 0:
            legend_dict["Node Shape"] = f_node_shapes
        for node_size in node_sizes:
            for k, v in node_size.items():
                f_node_sizes[k] = v
        if len(f_node_sizes) > 0:
            legend_dict["Node Size"] = f_node_sizes
        return legend_dict

    def _build_default_stylesheet(self):
        with open(default_stylesheet_fn) as json_file:
            stylesheet = json.load(json_file)
        for shape in self._shape_h.node.shapes:
            stylesheet.append({
                'selector': '.' + shape,
                'style': {'shape': shape}})
        return stylesheet

    def _set_preset(self, functions):
        for func in functions:
            func()
        return functions
