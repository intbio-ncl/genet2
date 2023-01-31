import re
from rdflib import URIRef,DCTERMS
from app.visualiser.builder.design import DesignBuilder
from app.graph.utility.model.model import model
from app.enhancer.enhancer import Enhancer
from app.graph.utility.graph_objects.node import Node
from app.visualiser.builder.builders.editor.hierarchy import EditorHierarchyViewBuilder
from app.visualiser.builder.builders.editor.interaction import EditorInteractionViewBuilder
from app.visualiser.builder.builders.editor.interaction_genetic import EditorInteractionGeneticViewBuilder
from app.visualiser.builder.builders.editor.interaction_protein import EditorInteractionProteinViewBuilder
from app.visualiser.builder.builders.editor.interaction_verbose import EditorInteractionVerboseViewBuilder
from app.visualiser.builder.builders.editor.pruned import EditorPrunedViewBuilder
from app.visualiser.builder.builders.editor.full import EditorFullViewBuilder

class EditorBuilder(DesignBuilder):
    def __init__(self, graph):
        super().__init__(graph)
        self._enhancer = Enhancer(self._graph)

    def set_full_view(self):
        self._view_builder = EditorFullViewBuilder(self._dg)

    def set_pruned_view(self):
        self._view_builder = EditorPrunedViewBuilder(self._dg)
         
    def set_hierarchy_view(self):
        self._view_builder = EditorHierarchyViewBuilder(self._dg)

    def set_interaction_verbose_view(self):
        self._view_builder = EditorInteractionVerboseViewBuilder(self._dg)

    def set_interaction_view(self):
        self._view_builder = EditorInteractionViewBuilder(self._dg)

    def set_interaction_genetic_view(self):
        self._view_builder = EditorInteractionGeneticViewBuilder(self._dg)

    def set_interaction_protein_view(self):
        self._view_builder = EditorInteractionProteinViewBuilder(self._dg)
        
    def get_io_nodes(self, predicate):
        inputs = {}
        outputs = {}
        i_p = {}
        o_p = {}
        def add_range(code,pred,container):
            range = model.get_range(code)
            if range == []:
                return 
            range = model.get_union(range[0])
            for r in model.resolve_union(range[0][0]):
                r_k = r[1][0]
                r = str(r[1][1]["key"])
                container[pred] += ([r] + [str(k[1]["key"])for k in model.get_derived(r_k)])
        def add_domain(code,pred,container):
            domain = model.get_domain(code)
            if domain == []:
                return
            domain = model.get_union(domain[0])
            for d in model.resolve_union(domain[0][0]):
                d_k = d[1][0]
                d = str(d[1][1]["key"])
                container[pred] += ([d] + [str(k[1]["key"])for k in model.get_derived(d_k)])
                
        int = model.get_class_code(model.identifiers.objects.interaction)
        pcc = model.get_class_code(URIRef(predicate))
        if model.is_derived(predicate, int):
            i, o = model.interaction_predicates(pcc)
            for inp in i:
                cc = inp[0]
                pred =str(inp[1]["key"])
                i_p[pred] = []
                add_range(cc,pred,i_p)
            for out in o:
                cc = out[0]
                pred =str(out[1]["key"])
                o_p[pred] = []
                add_range(cc,pred,o_p)
        else:
            inputs["subject"] = []
            outputs["object"] = []
            i_p["subject"] = []
            o_p["object"] = []
            try:
                cc = model.get_class_code(predicate)
            except ValueError:
                return [], []
            add_domain(cc,"subject",i_p)
            add_range(cc,"object",o_p)
        for node in self.get_view_nodes():
            t = node.get_type()
            if t == "None":
                continue
            for k,v in i_p.items():
                if v == [] or t in v:
                    if k in inputs:
                        inputs[k].append(node)
                    else:
                        inputs[k] = [node]
            for k,v in o_p.items():
                if v == [] or t in v:
                    if k in outputs:
                        outputs[k].append(node)
                    else:
                        outputs[k] = [node]
        return inputs,outputs

    def get_view_nodes(self, identifier=None):
        return self.view.get_node(identifier)

    def get_view_node_types(self):
        return [str(s) for s in self._view_builder.get_node_types()]

    def get_view_edge_types(self):
        return [str(s) for s in self._view_builder.get_edge_types()]

    def add_edges(self, n, v, e):
        # To reduce number of queries to server.
        all_nodes = []
        for node in n.values():
            all_nodes.append(node)
        for vertex in v.values():
            all_nodes.append(vertex)
        all_nodes = self._dg.nodes(all_nodes)
        all_nodes = {n.get_key(): n for n in all_nodes}
        n = {k:all_nodes[v] if isinstance(v,str) else v for k,v in n.items()}
        v = {k:all_nodes[v] if isinstance(v,str) else v for k,v in v.items()}
        edges = self._view_builder.transform(n,v,e)
        for n,v,e,p in edges:
            self._add_props(n)
            self._add_props(v)
        if len(edges) > 0:
            self._dg.add_edges(edges)

    def add_node(self, key, type,**kwargs):
        self._dg.add_node(key, type, name=_get_name(key),**kwargs)

    def _add_props(self,node):
        node.update({"name" :_get_name(node.get_key()),
                      "graph_name" : self._dg.name})

def _get_name(subject):
    split_subject = _split(str(subject))
    if len(split_subject[-1]) == 1 and split_subject[-1].isdigit():
        return split_subject[-2]
    else:
        return split_subject[-1]


def _split(uri):
    return re.split('#|\/|:', uri)
