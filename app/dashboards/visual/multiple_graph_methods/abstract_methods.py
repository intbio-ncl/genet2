
def set_key_connect(self):
    '''
    Connects nodes and edges based on full URI
    '''
    self._builder.connect_label = "key"


def set_display_name_connect(self):
    '''
    Connects nodes and edges based on display name
    '''
    self._builder.connect_label = "display_name"


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
    
def set_graph_number_node_color(self):
    '''
    All node colors pertain to the number 
    of the source graph when loaded.
    '''
    if self.node_color == self.set_graph_number_node_color:
        return self._color_h.node.graph_number()
    else:
        self.node_color = self.set_graph_number_node_color
