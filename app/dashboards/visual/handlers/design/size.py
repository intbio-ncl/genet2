from visual.handlers.abstract_size import AbstractSizeHandler
class SizeHandler(AbstractSizeHandler):
    def __init__(self,builder):
        super().__init__(builder)
        self._max_node_size = self._standard_node_size * 1.5
        self._modifier = 1.1

    def hierarchy(self):
        sizes = []
        for node,data in self._builder.v_nodes(data=True):
            if self._builder.get_rdf_type(node) is None:
                for n in [m[0] for m in self._builder.in_edges(node)]:
                    d = self._builder.get_entity_depth(n)
                    if d != 0:
                        break
            else:
                d = self._builder.get_entity_depth(node)
            if d == 0:
                s = self._max_node_size
            else:
                s = int(self._max_node_size / (d * self._modifier))
            sizes.append(s)
        return sizes


    