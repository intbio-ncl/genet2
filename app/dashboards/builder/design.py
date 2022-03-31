import os
import types

from rdflib import RDF

from app.graphs.viewgraph.design import DesignGraph 
from app.dashboards.builder.abstract import AbstractBuilder
from app.dashboards.builder.builders.design.view import ViewBuilder
from app.dashboards.builder.builders.design.mode import ModeBuilder

def _add_predicate(obj,predicate):
    method_name = f'get_{predicate.split("/")[-1].lower()}'
    def produce_get_predicate(predicate):
        def produce_get_predicate_inner(self,subject=None,lazy=False):
            return self._graph.edge_query(n=subject,e=predicate)
        return produce_get_predicate_inner
    obj.__dict__[method_name] = types.MethodType(produce_get_predicate(predicate),obj)

def _add_object(obj,subject):
    method_name = f'get_{subject.split("/")[-1].lower()}'
    def produce_get_subject(subject):
        def produce_get_subject_inner(self,lazy=False,children=True):
            if children:
                m_id = self._graph.model.get_class_code(subject)
                subjects = [str(subject),*[str(s[1]["key"]) for s in self._graph.model.get_derived(m_id)]]
            else:
                subjects = str(subject)
            return self._graph.edge_query(e=RDF.type, v=subjects)
        return produce_get_subject_inner
    obj.__dict__[method_name] = types.MethodType(produce_get_subject(subject),obj)

class DesignBuilder(AbstractBuilder):
    def __init__(self,graph):
        super().__init__(graph,DesignGraph)
        self._view_h = ViewBuilder(self)
        self._mode_h = ModeBuilder(self)
        for predicate in self._graph.model.identifiers.predicates:
            _add_predicate(self,predicate)
        for obj in self._graph.model.identifiers.objects:
            _add_object(self,obj)
    
    def get_entities(self):
        classes = [c[1]["key"] for c in self._graph.model.get_classes(False)]
        return self._graph.edge_query(v=classes,e=RDF.type)

    def get_children(self,node):
        cp = self._graph.model.get_child_predicate()
        return self._graph.edge_query(n=node,e=cp)
    
    def get_parents(self,node):
        cp = self._graph.model.get_child_predicate()
        return [e.n for e in self._graph.edge_query(v=node,e=cp)]
        
    def get_interaction_io(self,subject):
        inputs = []
        outputs = []
        nv_ns = self._graph.model.identifiers.namespaces.nv
        d_predicate = self._graph.model.identifiers.predicates.direction
        i_predicate = self._graph.model.identifiers.objects.input
        o_predicate = self._graph.model.identifiers.objects.output
        for edge in self._graph.edge_query(n=subject):
            labels = []
            for l in  edge.get_labels():
                # Knowledge of data model tricks to reduce pointless computation.
                if os.path.commonprefix([l,nv_ns]) != nv_ns:
                    continue
                if self._graph.model.identifiers.predicates.consistsOf == l:
                    continue
                labels.append(l)
            model_code = [self._graph.model.get_class_code(l) for l in labels]
            for d in [d[1] for d in self._graph.model.search((model_code,d_predicate,None))]:
                d,d_data = d
                if d_data["key"] == i_predicate:
                    inputs.append(edge)
                elif d_data["key"] == o_predicate:
                    outputs.append(edge)
                else:
                    raise ValueError(f'{labels} has direction not input or output')
        return inputs,outputs
            
    def get_entity_depth(self,subject):
        def _get_class_depth(s,depth):
            parent = self.get_parents(s)
            if parent == []:
                return depth
            depth += 1
            c_identifier = parent[0]
            return _get_class_depth(c_identifier,depth)
        return _get_class_depth(subject,0)

    def get_root_entities(self):
        roots = []
        for entity in self.get_entities():
            if self.get_parents(entity.n) == []:
                roots.append(entity.n)
        return roots



    def set_pruned_view(self):
        self.view = self._view_h.pruned()
         
    def set_hierarchy_view(self):
        self.view = self._view_h.hierarchy()

    def set_interaction_explicit_view(self):
        self.view = self._view_h.interaction_explicit()

    def set_interaction_verbose_view(self):
        self.view = self._view_h.interaction_verbose()

    def set_interaction_view(self):
        self.view = self._view_h.interaction()

    def set_interaction_genetic_view(self):
        self.view = self._view_h.interaction_genetic()

    def set_interaction_protein_view(self):
        self.view = self._view_h.interaction_protein()

    def set_interaction_io_view(self):
        self.view = self._view_h.interaction_io()

    def set_module_view(self):
        self.view = self._view_h.module_view()
