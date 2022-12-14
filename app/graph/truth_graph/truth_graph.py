import json
from app.graph.utility.model.model import model
from app.graph.design_graph.design_graph import DesignGraph
from app.graph.truth_graph.modules.synonym import SynonymModule
from app.graph.truth_graph.modules.interaction import InteractionModule
from app.graph.utility.graph_objects.node import Node
from app.graph.utility.graph_objects.edge import Edge
p_confidence = str(model.identifiers.external.confidence)
p_synonym = str(model.identifiers.external.synonym)

class TruthGraph(DesignGraph):
    def __init__(self, name, driver):
        super().__init__(driver,name)
        self.synonyms = SynonymModule(self)
        self.interactions = InteractionModule(self)
        self._np = {"graph_name": self.name}

    def add_node(self,key,type=None,**kwargs):
        kwargs.update(self._np)
        return super().add_node(key,type,**kwargs)

    def add_edges(self, edges, modifier):
        if not isinstance(edges,list):
            edges = [edges]
        if modifier <= 0:
            return
        uedges = []
        for e in edges:
            if not isinstance(e,Edge):
                e = Edge(*e)
            e = self._add_edge_gn(e)
            e.update({p_confidence: modifier})
            uedges.append(e)
        super().add_edges(uedges)

    def set_confidence(self, edge, confidence):
        self.driver.set_edge(edge, {p_confidence: confidence})
        return self.driver.submit()

    def node_query(self, n=[], **kwargs):
        return self._node_query(n,**kwargs)

    def edge_query(self, n=None, v=None, e=None, threshold=0, **kwargs):
        n = self._add_node_gn(n)
        v = self._add_node_gn(v)
        return [e for e in self._edge_query(n,e,v,**kwargs) 
                if int(e[p_confidence]) >= threshold]


    def load(self, fn):
        def _node(ele):
            k, t = self.driver.derive_key_type(ele["labels"])
            iden = ele["id"]
            if "properties" in ele:
                props = ele["properties"]
            else:
                props = self._np
            return Node(k, t, id=iden, **props)
        data = []
        with open(fn) as f:
            # Weirdness its always 1 line.
            for line in f:
                data = json.loads(line)
        for d in data:
            if d["type"] == "relationship":
                n = _node(d["start"])
                v = _node(d["end"])
                t = d["label"]
                props = d["properties"]
                iden = d["id"]
                self.driver.add_edge(n, v, t, id=iden, **props)
            elif d["type"] == "node":
                self.driver.add_node(_node(d))
            else:
                raise ValueError(f'{d["type"]} isnt known.')
        self.driver.submit()

    def _add_edge_gn(self, edge):
        gnd = self._np
        edge.n.update(gnd)
        edge.v.update(gnd)
        edge.update(gnd)
        return edge

    def _add_node_gn(self, node):
        if node is not None:
            gnd = self._np
            node.update(gnd)
            return node
        return None
