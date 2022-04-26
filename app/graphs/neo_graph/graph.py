from abc import ABC
from re import sub
from graphdatascience import GraphDataScience
from neo4j.data import Record
from neo4j.graph import Node as NeoNode
from neo4j.graph import Relationship

from app.graphs.neo_graph.utility.query_builder import QueryBuilder
from app.graphs.neo_graph.model.model import ModelGraph
from app.graphs.neo_graph.converter.handler import convert
from app.graphs.graph_objects.node import Node
from app.graphs.graph_objects.edge import Edge

modes = ["ignore","merge","duplicate","overwrite"]
class Graph:
    def __init__(self):
        self.driver = GraphDataScience("bolt://localhost:7687", auth=("neo4j", "Radeon12300"))
        self.qry_builder = QueryBuilder()
        self.model = ModelGraph()

    # -- WRITE --
    def submit(self):
        for qry_str in self.qry_builder.generate():
            self._run(qry_str)

    def add_graph(self, filename, mode="ignore", name=""):
        return convert(self, filename, mode, name)

    def add_node(self, *args, mode="ignore", **kwargs):
        n = self._node(args, kwargs)
        if self.qry_builder.is_node_staged(n):
            self.qry_builder.update_node(n)
            return n
        q_node = self.node_query(n)
        if mode != "duplicate" and q_node != []:
            q_node = q_node[0]
            self.qry_builder.add_match_node(q_node)
            q_node_props = q_node.get_properties()
            n_props = n.get_properties().copy()
            if mode == "merge" and q_node_props != n_props:
                new_props = self._new_props(q_node_props,n_props)
                self.qry_builder.add_set_node(n,new_props)
            elif mode == "overwrite" and q_node_props != n_props:
                new_props = self._new_props(q_node_props,n_props)
                self.qry_builder.add_replace_node_properties(n,new_props)
        else:
            self.qry_builder.add_create_node(n)
        return n

    def add_edge(self, n, v, e, mode="ignore", **kwargs):
        n = self.add_node(n, mode=mode)
        v = self.add_node(v, mode=mode)
        e = self._edge(n, v, e, kwargs)
        if self.qry_builder.is_edge_staged(e):
            self.qry_builder.update_edge(e)
            return e
        q_edge = self.edge_query(e=e)
        if mode != "duplicate" and q_edge != []:
            q_edge = q_edge[0]
            self.qry_builder.add_match_edge(q_edge)
            q_edge_props = q_edge.get_properties()
            n_props = e.get_properties().copy()
            if mode == "merge" and q_edge_props != n_props:
                new_props = self._new_props(q_edge_props,n_props)
                self.qry_builder.add_set_edge(e,new_props)
            elif mode == "overwrite" and q_edge_props != n_props:
                new_props = self._new_props(q_edge_props,n_props)
                self.qry_builder.add_replace_edge_properties(e,new_props)
        else:
            self.qry_builder.add_create_edge(e)
        return e

    def purge(self):
        return self._run(self.qry_builder.purge())

    def remove_graph(self,graph_name):
        for node in self.get_all_nodes():
            gns = node["graph_name"]
            self.qry_builder.add_match_node(node)

            if graph_name not in gns:
                continue
            if len(gns) == 1:
                self.qry_builder.add_remove_node(node)
            else:
                self.qry_builder.add_remove_node_property(node,{"graph_name":[graph_name]})
                for edge in self.edge_query(n=node):
                    props = edge.get_properties()
                    assert ("graph_name" in props)
                    self.qry_builder.add_match_edge(edge)
                    self.qry_builder.add_remove_edge_property(edge,{"graph_name":[graph_name]})
                
        for qry_str in self.qry_builder.generate():
            self._run(qry_str)
    
    # -- QUERY --
    def run_query(self,cypher_str):
        results = []
        def _node(item):
            properties = dict(item).copy()
            properties["id"] = item.id
            return self._node(item.labels,properties)

        for index,r in self._run(cypher_str).iterrows():
            record = {}
            for k,v in r.items():
                if isinstance(v,NeoNode):
                    record[k] = _node(v)
                elif isinstance(v,Relationship):
                    n = _node(v.start_node)
                    n1 = _node(v.end_node)
                    e_props = self._go_dict(v)
                    record[k] = self._edge(n,n1, v.type, e_props)
                else:
                    record[k] = v
            results.append(record)
        return results

    def node_query(self, identity=None, **kwargs):
        qry = self.qry_builder.node_query(identity, **kwargs)
        results = []
        for index,record in self._run(qry).iterrows():
            for k, v in record.items():
                props = self._go_dict(v)
                results.append(self._node(v.labels, props))
        return results

    def contains_node(self, node):
        return self.node_query(node.get_labels()) != []

    def contains_edge(self, edge):
        return self.edge_query(n=edge.n, v=edge.v, e=edge.get_labels()) != []

    def get_modes(self):
        return modes

    def edge_query(self, n=None, v=None, e=None, n_props={}, v_props={}, e_props={}):
        if isinstance(e, Edge):
            if n is None:
                n = e.n
            if v is None:
                v = e.v
            e = e.get_labels()
        qry = self.qry_builder.edge_query(n, v, e, n_props, v_props, e_props)
        print(qry)
        results =  []
        for index,record in self._run(qry).iterrows():
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

    def get_graph_names(self):
        gns = []
        for index,sublist in self._run(self.qry_builder.get_property(prop="graph_name")).iteritems():
            for k,v in sublist.items():
                gns += v
        return list(set(gns))

    def count_edges(self):
        result = self._run(self.qry_builder.count_edges())
        return result.pop(0).value()

    # -- Procedures --
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

    def degree(self,node):
        qry = self._graph.qry_builder.degree(node.labels, **node.get_properties())
        res = self._graph._run(qry)
        return res[0]["output"]

    def is_dense(self,node):
        qry = self._graph.qry_builder.is_dense(node.labels, **node.get_properties())
        res = self._graph._run(qry)
        return res[0]["output"]

    def is_connected(self, node,vetex):
        qry = self._graph.qry_builder.is_connected(node.labels, vetex.labels, node.get_properties(), vetex.get_properties())
        res = self._graph._run(qry)
        return res[0]["output"]

    def get_save_formats(self):
        return []
        
    def _run(self, cypher_str):
        if len(cypher_str) == 0:
            print("WARN:: Empty Cypher Query Entered.")
            return []
        return self.driver.run_cypher(cypher_str)

    def _go_dict(self, go):
        props = dict(go)
        props["id"] = go.id
        return props

    def _node(self, labels, properties):
        if len(labels) == 1 and isinstance(list(labels)[0], Node):
            n = labels[0]
        else:
            n = Node(list(labels), **properties)
        if n in self.qry_builder.nodes:
            n = self.qry_builder.nodes[n].graph_object
        return n

    def _edge(self, n, v, e, properties):
        if isinstance(e, Edge):
            return e
        return Edge(n, v, e, **properties)

    def _new_props(self,old_props,new_props):
        final_props = {}
        for k,v in new_props.items():
            if k in old_props:
                if isinstance(v,list):
                    ind = 0
                    while ind < len(v):
                        item = v[ind]
                        if item in old_props[k]:
                            v.pop(ind)
                        else:
                            ind +=1
                    if len(v) > 0:
                        final_props[k] = v
                else:
                    final_props[k] = v
            else:
                final_props[k] = v
        return final_props