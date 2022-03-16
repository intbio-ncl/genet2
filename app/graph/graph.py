from neo4j import GraphDatabase

from app.graph.utility.query_builder import QueryBuilder
from app.graph.utility.settings import SettingsManager
from app.graph.graph_objects.node import Node
from app.graph.graph_objects.edge import Edge
from app.graph.model.model import ModelGraph
from app.graph.converter.handler import convert

class Graph:
    def __init__(self):
        self.driver = GraphDatabase.driver(
            "bolt://localhost:7687", auth=("neo4j", "radeon12300"))
        self.qry_builder = QueryBuilder()
        self._settings = SettingsManager(self)
        self._model = ModelGraph()

    def add_node(self, *args, mode="ignore",**kwargs):
        n = self._node(args, kwargs)
        if self.qry_builder.is_node_staged(n):
            self.qry_builder.update_node(n)
            return n
        q_node = self.node_query(n)
        if mode != "duplicate" and q_node != []: 
            q_node = q_node[0]
            self.qry_builder.add_existing_node(q_node)
            if mode == "merge" and q_node.get_properties() != n.get_properties():
                self.qry_builder.add_node_update(n)
            elif mode == "overwrite" and q_node.get_properties() != n.get_properties():
                self.qry_builder.add_remove(n)
        else:
            self.qry_builder.add_node(n)
        return n

    def add_edge(self, n, v, e, mode="ignore",**kwargs):
        n = self.add_node(n,mode=mode)
        v = self.add_node(v,mode=mode)
        e = self._edge(n, v, e, kwargs)
        if self.qry_builder.is_edge_staged(e):
            self.qry_builder.update_edge(e)
            return e

        q_edge = self.edge_query(e=e)
        if mode != "duplicate" and q_edge != []: 
            q_edge = q_edge[0]
            self.qry_builder.add_existing_edge(q_edge)
            if mode == "merge" and q_edge.get_properties() != e.get_properties():
                self.qry_builder.add_edge_update(e)
            elif mode == "overwrite" and q_edge.get_properties() != e.get_properties():
                self.qry_builder.add_remove(e)
        else:
            self.qry_builder.add_edge(e)
        return e

    def submit(self):
        qry_str = self.qry_builder.generate()
        self._run(qry_str)

    def add_graph(self, filename,mode="ignore"):
        print(mode)
        return convert(self,filename,mode)

    def purge(self):
        return self._run(self.qry_builder.purge())

    def node_query(self, identity=None, **kwargs):
        qry = self.qry_builder.node_query(identity, **kwargs)
        results = []
        for record in self._run(qry):
            for k, v in record.items():
                props = self._go_dict(v)
                results.append(self._node(v.labels, props))
        return results

    def contains_node(self,node):
        return self.node_query(node.get_labels()) != []

    def contains_edge(self,edge):
        return self.edge_query(n=edge.n,v=edge.v,e=edge.get_labels()) != []

    def edge_query(self, n=None, v=None, e=None, n_props={}, v_props={}, e_props={}):
        if isinstance(e,Edge):
            e = e.get_labels()
        qry = self.qry_builder.edge_query(n, v, e, n_props, v_props, e_props)
        results = []
        for record in self._run(qry):
            n = record["n"]
            v = record["v"]
            e = record["e"]
            n_props = self._go_dict(n)
            v_props = self._go_dict(v)
            e_props = self._go_dict(e)
            results.append(self._edge(self._node(n.labels, n_props),
                           self._node(v.labels, v_props), e.type, e_props))
        return results

    def get_all_nodes(self):
        return self.node_query()

    def get_all_edges(self):
        return self.edge_query()

    def count_edges(self):
        result = self._run(self.qry_builder.count_edges())
        return result.pop(0).value()

    def shortest_path(self, n, v):
        qry = self.qry_builder.shortest_path(n, v)
        results = []
        for record in self._run(qry):
            path = record["p"]
            for edge in path:
                n = edge.start_node
                v = edge.end_node
                n_props = self._go_dict(n)
                v_props = self._go_dict(v)
                e_props = self._go_dict(edge)
                results.append(self._edge(self._node(n.labels, n_props),
                                          self._node(v.labels, v_props), edge.type, e_props))
        return results

    def cycles(self, n):
        cycles = []
        qry = self.qry_builder.cycles(n.labels, **n.get_properties())
        for record in self._run(qry):
            cycle = []
            path = record["path"]
            for edge in path:
                n = edge.start_node
                v = edge.end_node
                n_props = self._go_dict(n)
                v_props = self._go_dict(v)
                e_props = self._go_dict(edge)
                cycle.append(self._edge(self._node(n.labels, n_props),
                                        self._node(v.labels, v_props), edge.type, e_props))
            cycles.append(cycle)
        return cycles

    def k_spanning_tree(self, n, e=None, max_level=-1):
        paths = []
        edge_filters = []
        if e is not None:
            if not isinstance(e, (list, set, tuple)):
                e = [e]
            for edge in e:
                if isinstance(edge, Edge):
                    edge_filters += edge.labels
                else:
                    edge_filters.append(edge)

        qry = self.qry_builder.k_spanning_tree(
            n.labels, edge_filters, max_level=max_level, **n.get_properties())
        for record in self._run(qry):
            path = []
            for edge in record["path"]:
                n = edge.start_node
                v = edge.end_node
                n_props = self._go_dict(n)
                v_props = self._go_dict(v)
                e_props = self._go_dict(edge)
                path.append(self._edge(self._node(n.labels, n_props),
                            self._node(v.labels, v_props), edge.type, e_props))
            paths.append(path)
        return paths

    def collapse(self, n=None, v=None, edges=[], n_props={}, v_props={}):
        res = []
        nn_props = n.properties if n_props == {} and n is not None else {}
        vv_props = v.properties if v_props == {} and v is not None else {}
        nn_props.update(n_props)
        vv_props.update(v_props)
        n = n.labels if n is not None else []
        v = v.labels if v is not None else []
        qry = self.qry_builder.collapse(n, v, edges, nn_props, vv_props)
        for record in self._run(qry):
            edge = record["rel"]
            n = edge.start_node
            v = edge.end_node
            n_props = self._go_dict(n)
            v_props = self._go_dict(v)
            e_props = self._go_dict(edge)
            res.append(self._edge(self._node(n.labels, n_props),
                                  self._node(v.labels, v_props), edge.type, e_props))
        return res
        
    def _run(self, cypher_str):
        try:
            with self.driver.session() as s_graphDB:
                return list(s_graphDB.run(cypher_str))
        except ValueError as ex:
            print("WARN:: Empty Cypher Query Entered.")
            return []

    def _go_dict(self, go):
        props = dict(go)
        props["id"] = go.id
        return props

    def _node(self, labels, properties):
        if len(labels) == 1 and isinstance(list(labels)[0],Node):
            return labels[0]
        return Node(self, list(labels), **properties)

    def _edge(self, n, v, e, properties):
        if isinstance(e,Edge):
            return e
        return Edge(self, n, v, e, **properties)
