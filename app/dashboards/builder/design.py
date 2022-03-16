import os
import types

from rdflib import RDF

from graph.design import DesignGraph
from converters.design_handler import convert as i_convert
from converters.model_handler import convert as m_convert

from builder.abstract import AbstractBuilder
from builder.builders.design.view import ViewBuilder
from builder.builders.design.mode import ModeBuilder

def _add_predicate(obj,predicate):
    method_name = f'get_{predicate.split("/")[-1].lower()}'
    def produce_get_predicate(predicate):
        def produce_get_predicate_inner(self,subject=None,lazy=False):
            return self._graph.search((subject,predicate,None),lazy)
        return produce_get_predicate_inner
    obj.__dict__[method_name] = types.MethodType(produce_get_predicate(predicate),obj)

def _add_object(obj,subject):
    method_name = f'get_{subject.split("/")[-1].lower()}'
    def produce_get_subject(subject):
        def produce_get_subject_inner(self,lazy=False,children=True):
            if children:
                m_id = self._model_graph.get_class_code(subject)
                subjects = [subject,*[s[1]["key"] for s in self._model_graph.get_derived(m_id)]]
            else:
                subjects = subject
            return self._graph.search((None,RDF.type,subjects),lazy)
        return produce_get_subject_inner
    obj.__dict__[method_name] = types.MethodType(produce_get_subject(subject),obj)

class DesignBuilder(AbstractBuilder):
    def __init__(self,model,graph=None):
        model_graph = m_convert(model)
        super().__init__(i_convert(model_graph))
        self._model_graph = model_graph
        if graph:
            self.load(graph)
        self._view_h = ViewBuilder(self)
        self._mode_h = ModeBuilder(self)
        for predicate in self._model_graph.identifiers.predicates:
            _add_predicate(self,predicate)
        for obj in self._model_graph.identifiers.objects:
            _add_object(self,obj)
    
    def load(self,fns):
        if not isinstance(fns,(set,list,tuple)):
            fns = [fns]
        if not self._graph:
            self._graph = DesignGraph()
        for fn in fns:
            self._graph.add_graph(i_convert(self._model_graph,fn))

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

    def get_children(self,subject):
        subject = self._resolve_subject(subject)
        cp = self._model_graph.get_child_predicate()
        return [c[1:3] for c in self._graph.search((subject,cp,None))]
    
    def get_parents(self,subject):
        subject = self._resolve_subject(subject)
        cp = self._model_graph.get_child_predicate()
        return [c[0:3:2] for c in self._graph.search((None,cp,subject))]
        
    def get_entities(self):
        classes = [c[1]["key"] for c in self._model_graph.get_classes(False)]
        return [c[0] for c in self._graph.search((None,RDF.type,classes))]
    
    def get_interaction_io(self,subject):
        subject = self._resolve_subject(subject)
        inputs = []
        outputs = []
        nv_ns = self._model_graph.identifiers.namespaces.nv
        d_predicate = self._model_graph.identifiers.predicates.direction
        i_predicate = self._model_graph.identifiers.objects.input
        o_predicate = self._model_graph.identifiers.objects.output
        for obj,pred in [c[1:] for c in self._graph.search((subject,None,None))]:
            # Knowledge of data model tricks to reduce pointless computation.
            if os.path.commonprefix([pred, nv_ns]) != nv_ns:
                continue
            if pred == self._model_graph.identifiers.predicates.consistsOf:
                continue
            model_code = self._model_graph.get_class_code(pred)
            for d in [d[1] for d in self._model_graph.search((model_code,d_predicate,None))]:
                d,d_data = d
                if d_data["key"] == i_predicate:
                    inputs.append([obj,pred])
                elif d_data["key"] == o_predicate:
                    outputs.append([obj,pred])
                else:
                    raise ValueError(f'{pred} has direction not input or output')
        return inputs,outputs
            

    def get_entity_depth(self,subject):
        def _get_class_depth(s,depth):
            parent = self.get_parents(s)
            if parent == []:
                return depth
            depth += 1
            c_identifier = parent[0][0][0]
            return _get_class_depth(c_identifier,depth)
        return _get_class_depth(subject,0)

    def get_root_entities(self):
        roots = []
        for entity in self.get_entities():
            if self.get_parents(entity[0]) == []:
                roots.append(entity)
        return roots