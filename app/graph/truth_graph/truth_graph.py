import json
import re

from app.graph.utility.model.model import model
from app.graph.truth_graph.modules.synonym import SynonymModule
from app.graph.utility.graph_objects.node import Node
from app.graph.utility.graph_objects.edge import Edge
p_confidence = str(model.identifiers.external.confidence)
p_synonym = str(model.identifiers.external.synonym)


class TruthGraph:
    def __init__(self, name, driver):
        self.name = [name]
        self.synonyms = SynonymModule(self)
        self.driver = driver
        self._np = {"graph_name": self.name}

    def nodes(self, n=None, **kwargs):
        return self._node_query(n, **kwargs)

    def edges(self, n=None, v=None, e=None):
        return self._edge_query(n=n, v=v, e=e)

    def add_edge(self, edge, modifier):
        if modifier < 0:
            return
        e = self._add_edge_gn(edge)
        e.update({p_confidence: modifier})
        self.driver.add_edge(e.n, e.v, e.get_type(), **e.get_properties())
        self.driver.submit()

    def add_node(self, node):
        node.update(self._np)
        n_props = node.get_properties()
        if "name" not in n_props:
            node.update({"name": _get_name(node.get_key())})
        self.driver.add_node(node)
        self.driver.submit()

    def remove_node(self, node):
        node.update(self._np)
        self.driver.remove_node(node)
        return self.driver.submit()

    def remove_edge(self, edge):
        edge = self._add_edge_gn(edge)
        self.driver.remove_edge(edge.n,edge.v,edge.get_type(),**edge.get_properties())
        return self.driver.submit()

    def set_confidence(self, edge, confidence):
        self.driver.set_edge(edge, {p_confidence: confidence})
        return self.driver.submit()

    def node_query(self, n=[], **kwargs):
        return self.driver.node_query(n, graph_name=self.name, **kwargs)

    def edge_query(self, n=None, v=None, e=None, threshold=0, **kwargs):
        n = self._add_node_gn(n)
        v = self._add_node_gn(v)
        return [e for e in self.driver.edge_query(n=n, v=v, e=e,
                                                  e_props=self._np,
                                                  **kwargs)
                if int(e[p_confidence]) >= threshold]

    def export(self, out_name):
        res = self.driver.export(self.name)
        res_l = []
        for r in res.splitlines():
            res_l.append(json.loads(r))
        with open(out_name, 'w') as f:
            json.dump(res_l, f)
        return out_name

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

    def _seed_graph(self):
        # TODO: Add some initial data into graph.
        pass

    def _node_query(self, n=None, **kwargs):
        if None in self.name:
            return []
        return self.driver.node_query(n, graph_name=self.name, **kwargs)

    def _edge_query(self, n=None, e=None, v=None, **kwargs):
        if None in self.name:
            return []
        props = {"graph_name": self.name}
        return self.driver.edge_query(n=n, v=v, e=e, e_props=props, n_props=props, v_props=props, **kwargs)

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
