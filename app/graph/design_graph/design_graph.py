import types
from rdflib import RDF
from app.graph.utility.model.model import model
from app.graph.design_graph.gds.project import ProjectBuilder
from app.graph.design_graph.gds.procedures import Procedures

def _add_predicate(obj,predicate):
    method_name = f'get_{predicate.split("/")[-1].lower()}'
    def produce_get_predicate(predicate):
        def produce_get_predicate_inner(self,subject=None):
            return self._edge_query(n=subject,e=predicate)
        return produce_get_predicate_inner
    obj.__dict__[method_name] = types.MethodType(produce_get_predicate(predicate),obj)

def _add_object(obj,subject):
    method_name = f'get_{subject.split("/")[-1].lower()}'
    def produce_get_subject(subject):
        def produce_get_subject_inner(self):
            derived = ([subject] + [n[1]["key"] for n in model.get_derived(subject)])
            return self._node_query(derived)
        return produce_get_subject_inner
    obj.__dict__[method_name] = types.MethodType(produce_get_subject(subject),obj)

class DesignGraph:
    def __init__(self,driver,name,predicate="ALL"):
        if not isinstance(name,list):
            name = [name]
        self.name = name
        self.driver = driver
        self.procedure = Procedures(self)
        self.project = ProjectBuilder(self)

        self._predicate=predicate
        for c in model.get_classes(False):
            _add_object(self,c[1]["key"])
        for p in model.get_properties():
            _add_predicate(self,p[1]["key"])

    def drop(self):
        self.driver.remove_graph(self.name)
    
    def nodes(self,**kwargs):
        return self._node_query(**kwargs)

    def edges(self,n=None,v=None,e=None,directed=True,exclusive=False):
        return self._edge_query(n=n,v=v,e=e,directed=directed,exclusive=exclusive)
        
    def get_children(self,node):
        cp = model.get_child_predicate()
        return self._edge_query(n=node,e=cp)
    
    def get_parents(self,node):
        cp = model.get_child_predicate()
        return self._edge_query(n=node,e=cp)

    def get_entity_depth(self,subject):
        def _get_class_depth(s,depth):
            parent = self.get_parents(s)
            if parent == []:
                return depth
            depth += 1
            c_identifier = parent[0].n
            return _get_class_depth(c_identifier,depth)
        return _get_class_depth(subject,0)

    def get_root_entities(self):
        roots = []
        for node in self.get_entity():
            if self.get_parents(node) == []:
                roots.append(node)
        return roots
    
    def get_interaction_io(self,subject):
        inputs = []
        outputs = []
        d_predicate = model.identifiers.predicates.direction
        i_predicate = model.identifiers.objects.input
        o_predicate = model.identifiers.objects.output
        for edge in self._edge_query(n=subject):
            e_type = edge.get_type()
            model_code = model.get_class_code(e_type)
            for d in [d[1] for d in model.search((model_code,d_predicate,None))]:
                d,d_data = d
                if d_data["key"] == i_predicate:
                    inputs.append(edge)
                elif d_data["key"] == o_predicate:
                    outputs.append(edge)
                else:
                    raise ValueError(f'{subject} has direction not input or output')
        return inputs,outputs
            
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

    def get_project_graph(self,name):
        return self.project.get_graph(name)

    def _node_query(self,n=None,**kwargs):
        if None in self.name:
            return []
        return self.driver.node_query(n,predicate=self._predicate,graph_name=self.name,**kwargs)

    def _edge_query(self,n=None,e=None,v=None,**kwargs):
        if None in self.name:
            return []
        props = {"graph_name" : self.name}
        return self.driver.edge_query(n=n,v=v,e=e,
                e_props=props,n_props=props,v_props=props,
                predicate=self._predicate,**kwargs)