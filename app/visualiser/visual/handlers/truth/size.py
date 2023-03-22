from app.visualiser.visual.handlers.abstract_size import AbstractSizeHandler
class TruthSizeHandler(AbstractSizeHandler):
    def __init__(self,builder):
        super().__init__(builder)
        self._max_node_size = self._standard_node_size * 1.5
        self._modifier = 1.1

    def hierarchy(self):
        sizes = []
        for node in self._builder.v_nodes():
            if node.get_type() == "None":
                for n in self._builder.in_edges(node):
                    d = self._builder.get_entity_depth(n.v)
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


    