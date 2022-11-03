
import json
import os
from app.graph.utility.graph_objects.node import Node
from app.graph.utility.graph_objects.edge import Edge

default_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)),"logs")
class ChangeLogger:
    def __init__(self,log_dir=default_dir):
        self.log_dir = log_dir
        if not os.path.isdir(self.log_dir):
            os.mkdir(self.log_dir)
    
    def _get_gn(self,gn):
        fn = os.path.join(self.log_dir,"-".join(gn)+".json")
        if not os.path.isfile(fn):
            os.mknod(fn)
        return fn

    def _add_to_file(self,fn,d):
        with open(fn) as f:
            try:
                data = json.load(f)
            except json.decoder.JSONDecodeError:
                data = []
        data.append(d)
        json_object = json.dumps(data, indent=4)
        with open(fn, 'w') as f:
            f.write(json_object)

    def get_changes(self,graph_name):
        fn = self._get_gn(graph_name)
        with open(os.path.join(self.log_dir,fn)) as f:
            changes = json.load(f)
        for change in changes:
            for k,v in change.items():
                if isinstance(v,dict):
                    gt = v["graph_type"]
                    if gt == "node":
                        obj = Node(v["key"],v["type"],**v["properties"])
                    elif gt == "edge":
                        n1 = Node(v["n"]["key"],v["n"]["type"],**v["n"]["properties"])
                        n2 = Node(v["v"]["key"],v["v"]["type"],**v["v"]["properties"])
                        obj = Edge(n1,n2,v["key"],**v["properties"])
                    change[k] = obj
        return changes

    def remove_graph(self,graph_name):
        fn = self._get_gn(graph_name)
        os.remove(fn)
    
    def add_node(self,node,graph_name):
        fn = self._get_gn(graph_name)
        self._add_to_file(fn,{"action" : "add",
                           "subject": self._node_to_dict(node),
                           "type" : "node"})

    def replace_node(self,old,new,graph_name):
        fn = self._get_gn(graph_name)
        self._add_to_file(fn,{"action" : "replace",
                            "subject": old,
                            "predicate" : "uri",
                            "object" : new,
                            "type" : "node"})
    
    def replace_node_property(self,node,new_props,graph_name):
        fn = self._get_gn(graph_name)
        for k,v in new_props.items():
            self._add_to_file(fn,{"action" : "replace",
                                "subject": node.get_key(),
                                "predicate" : k,
                                "object" : v,
                                "type" : "node"})

    def remove_node(self,node,graph_name):
        fn = self._get_gn(graph_name)
        self._add_to_file(fn,{"action" : "remove",
                              "subject": node.get_key(),
                              "type" : "node"})


    def add_edge(self,edge,graph_name):
        fn = self._get_gn(graph_name)
        self._add_to_file(fn,{"action" : "add",
                              "subject": self._edge_to_dict(edge),
                              "type" : "edge"})
    
    def replace_edge(self,old,new,graph_name):
        fn = self._get_gn(graph_name)
        self._add_to_file(fn,{"action" : "replace",
                            "subject": old,
                            "predicate" : "uri",
                            "object" : new,
                            "type" : "edge"})
    
    def replace_edge_property(self,edge,new_props,graph_name):
        fn = self._get_gn(graph_name)
        for k,v in new_props.items():
            self._add_to_file(fn,{"action" : "replace",
                                "subject": self._edge_to_dict(edge),
                                "predicate" : k,
                                "object" : v,
                                "type" : "edge"})

    def remove_edge(self,edge,graph_name):
        fn = self._get_gn(graph_name)
        self._add_to_file(fn,{"action" : "remove",
                              "subject": self._edge_to_dict(edge),
                              "type" : "edge"})
                              
    def _node_to_dict(self,node):
        return {"key" : str(node.get_key()),
                "type" : str(node.get_type()),
                "properties" : node.get_properties(),
                "graph_type" : "node"}

    def _edge_to_dict(self,edge):
        return {"n" : self._node_to_dict(edge.n),
                "v" : self._node_to_dict(edge.v),
                "key" : edge.get_type(),
                "properties" : edge.get_properties(),
                "graph_type" : "edge"}
logger = ChangeLogger()


