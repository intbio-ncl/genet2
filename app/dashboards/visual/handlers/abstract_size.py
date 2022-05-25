class AbstractSizeHandler:
    def __init__(self,builder):
        self._builder = builder
        self._standard_node_size = 30


    def standard(self):
        return [self._standard_node_size for node in self._builder.v_nodes()]

    def class_type(self):
        node_sizes = []
        for node in self._builder.v_nodes():
            if node.get_type() == "None":
                node_sizes.append(self._standard_node_size/2)
            else:
                node_sizes.append(self._standard_node_size)
        return node_sizes

    def centrality(self):
        node_sizes = []
        for node in self._builder.v_nodes():
            node_size = 1 + len([*self._builder.in_edges(node)]) + len([*self._builder.out_edges(node)])
            node_size = int((node_size * self._standard_node_size) / 4)
            if node_size > 100:
                node_size = 100
            if node_size < self._standard_node_size/2:
                node_size = self._standard_node_size
            node_sizes.append(node_size)
        return node_sizes

    def in_centrality(self):
        node_sizes = []
        for node in self._builder.v_nodes():
            node_size = 1 + len([*self._builder.in_edges(node)])
            node_size = int((node_size * self._standard_node_size) / 2)
            if node_size > 100:
                node_size = 100
            if node_size < self._standard_node_size/2:
                node_size = self._standard_node_size
            node_sizes.append(node_size)
        return node_sizes

    def out_centrality(self):
        node_sizes = []
        for node in self._builder.v_nodes():
            node_size = 1 + len([*self._builder.out_edges(node)])
            node_size = int((node_size * self._standard_node_size) / 2)
            if node_size > 100:
                node_size = 100
            if node_size < self._standard_node_size/2:
                node_size = self._standard_node_size
            node_sizes.append(node_size)
        return node_sizes


    