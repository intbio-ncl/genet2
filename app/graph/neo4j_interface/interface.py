from graphdatascience import GraphDataScience
from neo4j.graph import Node as NeoNode
from neo4j.graph import Relationship

from  app.graph.utility.graph_objects.node import Node
from  app.graph.utility.graph_objects.edge import Edge
from  app.graph.neo4j_interface.query_builder import QueryBuilder
from  app.graph.neo4j_interface.gds.project import Projection
from  app.graph.neo4j_interface.gds.procedures import Procedures
from  app.graph.utility.model.model import model


class Neo4jInterface:
    def __init__(self):
        self.driver = GraphDataScience(
            "bolt://localhost:7687", auth=("neo4j", "Radeon12300"))
        self.qry_builder = QueryBuilder()
        self.project = Projection(self)
        self.procedures = Procedures(self)

    @property
    def nodes(self):
        for node in self.node_query():
            yield node

    @property
    def edges(self):
        for edge in self.edge_query():
            yield edge

    def submit(self):
        for qry_str in self.qry_builder.generate():
            self._run(qry_str)

    def add_node(self, key, ntype=None, mode="merge", **kwargs):
        n = self._node(key, ntype, kwargs)
        if self.qry_builder.is_node_staged(n):
            return n
        q_node = self.node_query(n)
        if mode == "duplicate" :
            self.qry_builder.add_create_node(n)
            return n
        if q_node != []:
            q_node = q_node[0]
            self.qry_builder.add_match_node(q_node)
            q_node_props = q_node.get_properties()
            n_props = n.get_properties().copy()
            if mode == "merge" and q_node_props != n_props:
                new_props = self._new_props(q_node_props, n_props)
                if new_props == {}:
                    return n
                self.qry_builder.add_set_node(n, new_props)
            elif mode == "overwrite" and q_node_props != n_props:
                new_props = self._new_props(q_node_props, n_props)
                self.qry_builder.add_replace_node_properties(n, new_props)
        else:
            self.qry_builder.add_create_node(n)
        return n

    def add_edge(self, n, v, e, mode="merge", **kwargs):
        n = self.add_node(n, mode=mode)
        v = self.add_node(v, mode=mode)
        e = self._edge(n, v, e, kwargs)
        if self.qry_builder.is_edge_staged(e):
            return e
        if mode == "duplicate":
            self.qry_builder.add_create_edge(e)
            return e
        q_edge = self.edge_query(e=e)
        if q_edge != []:
            q_edge = q_edge[0]
            self.qry_builder.add_match_edge(q_edge)
            q_edge_props = q_edge.get_properties()
            n_props = e.get_properties().copy()
            if mode == "merge" and q_edge_props != n_props:
                new_props = self._new_props(q_edge_props, n_props)
                if new_props == {}:
                    return e
                self.qry_builder.add_set_edge(e, new_props)
            elif mode == "overwrite" and q_edge_props != n_props:
                new_props = self._new_props(q_edge_props, n_props)
                self.qry_builder.add_replace_edge_properties(e, new_props)
        else:
            self.qry_builder.add_create_edge(e)
        return e

    def remove_edge(self,edge):
        self.qry_builder.add_match_edge(edge)
        self.qry_builder.add_remove_edge(edge)
    
    def remove_node(self,node,use_id=False):
        self.qry_builder.add_match_node(node,use_id)
        self.qry_builder.add_remove_node(node)

    def replace_edge_property(self,edge,new_properties):
        self.qry_builder.add_match_edge(edge)
        self.qry_builder.add_replace_edge_properties(edge, new_properties)
    
    def set_edge(self,edge,new_properties):
        self.qry_builder.add_match_edge(edge)
        self.qry_builder.add_set_edge(edge, new_properties)

    def add_node_label(self,node,label):
        self.qry_builder.add_match_node(node)
        self.qry_builder.add_add_node_label(node, label)

    def merge_nodes(self,edge):
        qry = self.qry_builder.merge_relationship_nodes(edge)
        res = self.run_query(qry)
        assert(len(res) == 1)
        return list(res[0].values())[0]

    def remove_graph(self, graph_name):
        if not isinstance(graph_name,list):
            graph_name = [graph_name]
        for node in self.nodes:
            if "graph_name" not in node.get_properties():
                continue
            gns = node["graph_name"]
            self.qry_builder.add_match_node(node)
            if len(set(graph_name) & set(gns)) == 0:
                continue
            if len(gns) == 1:
                self.qry_builder.add_remove_node(node)
            else:
                self.qry_builder.add_remove_node_property(
                    node, {"graph_name": [graph_name]})
                for edge in self.edge_query(n=node):
                    props = edge.get_properties()
                    if "graph_name" not in props:
                        continue
                    self.qry_builder.add_match_edge(edge)
                    self.qry_builder.add_remove_edge_property(
                        edge, {"graph_name": [graph_name]})
        for qry_str in self.qry_builder.generate():
            self._run(qry_str)

    def node_query(self, identity=None, predicate="ALL", **kwargs):
        qry = self.qry_builder.node_query(identity,predicate=predicate, **kwargs)
        results = []
        for index, record in self._run(qry).iterrows():
            for k, v in record.items():
                key, r_type = self._derive_key_type(v.labels)
                props = self._go_dict(v)
                results.append(self._node(key, r_type, props))
        return results

    def edge_query(self, n=None, v=None, e=None, n_props={}, v_props={}, e_props={}, directed=True, exclusive=False,predicate="ALL"):
        if isinstance(e, Edge):
            if n is None:
                n = e.n
            if v is None:
                v = e.v
            e = e.get_type()
        qry = self.qry_builder.edge_query(n, v, e, n_props.copy(), v_props.copy(),
                                          e_props.copy(), directed=directed, exclusive=exclusive,predicate=predicate)
        results = []
        for index, record in self._run(qry).iterrows():
            n = record["n"]
            v = record["v"]
            e = record["e"]
            nkey, n_type = self._derive_key_type(n.labels)
            vkey, v_type = self._derive_key_type(v.labels)
            n_props = self._go_dict(n)
            v_props = self._go_dict(v)
            e_props = self._go_dict(e)
            results.append(self._edge(self._node(nkey, n_type, n_props), self._node(
                vkey, v_type, v_props), e.type, e_props))
        return results

    def node_property(self,prop_name,distinct=False):
        qry = self.qry_builder.node_property(prop=prop_name,distinct=distinct)
        results = []
        for index, record in self._run(qry).iterrows():
            for k,v in record.items():
                if prop_name in k and v is not None:
                    if isinstance(v,list):
                        results +=v
                    else:
                        results.append(v)
        return results

    def labels_to_node(self, labels):
        return Node(*self._derive_key_type(labels))
    
    def get_isolated_nodes(self,**kwargs):
        results = []
        qry = self.qry_builder.get_isolated_nodes(**kwargs)
        for index,record in self._run(qry).iterrows():
            for k, v in record.items():
                key, r_type = self._derive_key_type(v.labels)
                props = self._go_dict(v)
                results.append(self._node(key, r_type, props))
        return results

    def run_query(self, cypher_str):
        results = []

        def _node(item):
            key, r_type = self._derive_key_type(item.labels)
            properties = dict(item).copy()
            properties["id"] = item.id
            return self._node(key, r_type, properties)

        for index, r in self._run(cypher_str).iterrows():
            record = {}
            for k, v in r.items():
                if isinstance(v, NeoNode):
                    record[k] = _node(v)
                elif isinstance(v, Relationship):
                    n = _node(v.start_node)
                    n1 = _node(v.end_node)
                    e_props = self._go_dict(v)
                    record[k] = self._edge(n, n1, v.type, e_props)
                else:
                    record[k] = v
            results.append(record)
        return results

    def _run(self, cypher_str):
        if len(cypher_str) == 0:
            #print("WARN:: Empty Cypher Query Entered.")
            return []
        return self.driver.run_cypher(cypher_str)

    def _node(self, name, ntype=None, properties={}):
        if isinstance(name, Node):
            n = name
        else:
            n = Node(name, ntype, **properties)
        if n in self.qry_builder.nodes:
            on = n
            n = self.qry_builder.nodes[n].graph_object
            if n.type == "None":
                n.type = on.type
        return n

    def _edge(self, n, v, e, properties):
        if isinstance(e, Edge):
            return e
        return Edge(n, v, e, **properties)

    def _derive_key_type(self, labels):
        labels = list(labels)
        if "None" in labels:
            k = [l for l in labels if l != "None"]
            return k[0],"None"
        res = model.are_classes(labels)
        n = zip(labels,res)
        k = []
        t = []
        for lab,ac in n:
            if ac:
                t.append(lab)
            else:
                k.append(lab)
        if len(k) == 1:
            k = k[0]
        if len(t) == 1:
            t = t[0]
        if len(k) == 0:
            k = t
        if t == []:
            return k,None
        return k,t

    def _go_dict(self, go):
        props = dict(go)
        props["id"] = go.id
        return props

    def _new_props(self, old_props, new_props):
        final_props = {}
        for k, v in new_props.items():
            if k in old_props:
                if isinstance(v, list):
                    ind = 0
                    while ind < len(v):
                        item = v[ind]
                        if item in old_props[k]:
                            v.pop(ind)
                        else:
                            ind += 1
                    if len(v) > 0:
                        final_props[k] = v
                else:
                    final_props[k] = v
            else:
                final_props[k] = v
        return final_props
