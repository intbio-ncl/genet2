import types
import re
import json
from rdflib import RDF,DCTERMS
from app.graph.utility.model.model import model
from app.graph.design_graph.gds.project import ProjectBuilder
from app.graph.design_graph.gds.procedures import Procedures
from app.graph.utility.graph_objects.node import Node
from app.graph.utility.graph_objects.edge import Edge

def _add_predicate(obj, pred):
    method_name = f'get_{pred.split("/")[-1].lower()}'
    def produce_get_predicate(pred):
        def produce_get_predicate_inner(self, subject=None,predicate="ALL"):
            return self._edge_query(n=subject, e=pred,predicate=predicate)
        return produce_get_predicate_inner
    obj.__dict__[method_name] = types.MethodType(
        produce_get_predicate(pred), obj)


def _add_object(obj, subject):
    method_name = f'get_{subject.split("/")[-1].lower()}'

    def produce_get_subject(subject):
        def produce_get_subject_inner(self,predicate="ALL"):
            derived = ([subject] + [n[1]["key"]
                       for n in model.get_derived(subject)])
            return self._node_query(derived,predicate=predicate)
        return produce_get_subject_inner
    obj.__dict__[method_name] = types.MethodType(
        produce_get_subject(subject), obj)


class DesignGraph:
    def __init__(self, driver, name, predicate="ALL"):
        if not isinstance(name, list):
            name = [name]
        self.name = name
        self.driver = driver
        self.procedure = Procedures(self)
        self.project = ProjectBuilder(self)

        for c in model.get_classes(False):
            _add_object(self, c[1]["key"])
        for p in model.get_properties():
            _add_predicate(self, p[1]["key"])

    def drop(self):
        self.driver.remove_graph(self.name)

    def nodes(self, n=None, **kwargs):
        return self._node_query(n,**kwargs)

    def edges(self, n=None, v=None, e=None, directed=True, exclusive=False):
        return self._edge_query(n=n, v=v, e=e, directed=directed, exclusive=exclusive)

    def add_node(self,key,type,sequence=None,description=None,**kwargs):
        if "graph_name" not in kwargs:
            kwargs["graph_name"] = self.name
        if sequence is not None:
            kwargs[model.identifiers.predicates.has_sequence] = sequence
        if description is not None:
            if not isinstance(description,list):
                description = [description]
            kwargs[DCTERMS.description] = description
        n = self.driver.add_node(key,type,**kwargs)
        self.driver.submit()
        return n
        
    def add_edges(self,edges):
        for edge in edges:
            if isinstance(edge,Edge):
                n = edge.n
                v = edge.v
                e = edge.get_type()
                props = edge.get_properties()
            elif len(edge) == 4:
                n,v,e,props = edge
            else:
                n,v,e = edge
                props = {}
            if "graph_name" not in props:
                props["graph_name"] = self.name
            if "graph_name" not in n.get_properties():
                n.add_property("graph_name",self.name)
            if "graph_name" not in v.get_properties():
                v.add_property("graph_name",self.name)
            
            self.driver.add_edge(n,v,e,**props)
        self.driver.submit()

    def remove_node(self,nodes):
        if not isinstance(nodes,list):
            nodes = [nodes]
        for node in nodes:
            if "graph_name" not in node.get_properties():
                node.update({"graph_name" : self.name})
            self.driver.remove_node(node)
        self.driver.submit()

    def remove_edges(self,edges):
        if not isinstance(edges,list):
            edges = [edges]
        for edge in edges:
            if isinstance(edge,Edge):
                n = edge.n
                v = edge.v
                e = edge.get_type()
                props = edge.get_properties()
            elif len(edge) == 4:
                n,v,e,props = edge
            else:
                n,v,e = edge
                props = {}
            if "graph_name" not in props:
                props["graph_name"] = self.name
            if "graph_name" not in n.get_properties():
                n.add_property("graph_name",self.name)
            if "graph_name" not in v.get_properties():
                v.add_property("graph_name",self.name)
            self.driver.remove_edge(n,v,e,**props)
        self.driver.submit()

        
    def replace_label(self,old,new):
        new_props = {"name" : _get_name(new)}
        self.driver.replace_node_label(old,new,new_props=new_props,graph_name=self.name)
        self.driver.submit()

    def replace_node_property(self,node,predicate,new):
        if "graph_name" not in node.get_properties():
            node.update({"graph_name" : self.name})
        self.driver.replace_node_property(node,{predicate:new})
        self.driver.submit()

    def replace_edge_property(self,edge,predicate,new):
        n,v,e,props = edge
        if "graph_name" not in props:
            edge.update({"graph_name" : self.name})
        self.driver.replace_edge_property(n,v,e,props,{predicate:new})
        self.driver.submit()
        
    def get_children(self, node):
        cp = model.get_child_predicate()
        return self._edge_query(n=node, e=cp)

    def get_parents(self, node):
        cp = model.get_child_predicate()
        return self._edge_query(v=node, e=cp)

    def get_by_type(self,types):
        return self._node_query(types)

    def get_entity_depth(self, subject):
        def _get_class_depth(s, depth):
            parent = self.get_parents(s)
            if parent == []:
                return depth
            depth += 1
            c_identifier = parent[0].n
            return _get_class_depth(c_identifier, depth)
        return _get_class_depth(subject, 0)

    def get_root_entities(self):
        roots = []
        for node in self.get_entity():
            if self.get_parents(node) == []:
                roots.append(node)
        return roots

    def get_leaf_entities(self):
        roots = []
        for node in self.get_entity():
            if self.get_children(node) == []:
                roots.append(node)
        return roots
        
    def get_interactions(self,node,predicate=None):
        s = model.identifiers.objects.interaction
        derived = ([s] + [n[1]["key"] for n in model.get_derived(s)])
        return self._edge_query(n=derived,v=node,e=predicate)

    def get_interaction_elements(self,interaction,predicate=None):
        if predicate is None:
            model_code = model.get_class_code(interaction.get_type())
            inp,out = model.interaction_predicates(model_code)
            predicate = [str(i[1]["key"]) for i in inp]
            predicate += [str(o[1]["key"]) for o in out]
            
        return self._edge_query(n=interaction,e=predicate)

    def get_interaction_io(self, subject):
        inputs = []
        outputs = []
        d_predicate = model.identifiers.predicates.direction
        i_predicate = model.identifiers.objects.input
        o_predicate = model.identifiers.objects.output
        for edge in self._edge_query(n=subject):
            e_type = edge.get_type()
            model_code = model.get_class_code(e_type)
            for d in [d[1] for d in model.search((model_code, d_predicate, None))]:
                d, d_data = d
                if d_data["key"] == i_predicate:
                    inputs.append(edge)
                elif d_data["key"] == o_predicate:
                    outputs.append(edge)
                else:
                    raise ValueError(
                        f'{subject} has direction not input or output')
        return inputs, outputs

    def get_interaction_directions(self,interaction):
        icc = model.get_class_code(interaction.get_type()) 
        idir = model.get_interaction_direction(icc)
        if idir == []:
            return []
        assert(len(idir) == 1)
        return idir[0]

    def get_isolated_nodes(self):
        if None in self.name:
            return []
        return self.driver.get_isolated_nodes(graph_name=self.name)
        
    def resolve_list(self, list_node):
        elements = []
        next_node = list_node
        while True:
            res = self._edge_query(n=next_node)
            f = [c for c in res if str(RDF.first) in c.get_type()]
            r = [c for c in res if str(RDF.rest) in c.get_type()]
            if len(f) != 1 or len(r) != 1:
                raise ValueError(f'{list_node} is a malformed list.')
            elements.append(f[0])
            r = r[0]
            if str(RDF.nil) in r.v.get_labels():
                break
            next_node = r.v
        return elements

    def get_project_preset_names(self):
        return self.project.get_presets()

    def get_projected_names(self):
        return self.project.get_projected_names()

    def get_project_graph(self, name):
        return self.project.get_graph(name)

    def export(self, out_name):
        res = self.driver.export(self.name)
        res_l = []
        for r in res.splitlines():
            res_l.append(json.loads(r))
        with open(out_name, 'w') as f:
            json.dump(res_l, f)
        return out_name

    def _node_query(self, n=None,predicate="ALL", **kwargs):
        if None in self.name:
            return []
        return self.driver.node_query(n, predicate=predicate, graph_name=self.name, **kwargs)

    def _edge_query(self, n=None, e=None, v=None, predicate="ALL", **kwargs):
        if None in self.name:
            return []
        props = {"graph_name": self.name}
        return self.driver.edge_query(n=n, v=v, e=e,
                                      e_props=props, n_props=props, v_props=props,
                                      predicate=predicate, **kwargs)


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