from app.converter.utility.identifiers import identifiers
from app.enhancer.data_miner.graph_analyser.utility.graph import SBOLGraph
from app.graph.utility.model.model import model
from app.converter.utility.common import map_to_nv
from rdflib import Graph

s_cd = identifiers.objects.component_definition
nv_characteristic = model.identifiers.predicates.hasCharacteristic
physical_entity = model.identifiers.roles.physical_entity
nv_role = model.identifiers.predicates.role
model_roots = model.get_base_class()

class GraphAnalyser:
    def __init__(self, db_handler):
        self._db_handler = db_handler

    def get_subject(self, graph, fragments=None):
        graph = SBOLGraph(graph)
        p_s = graph.get_component_definitions()
        if len(p_s) == 1:
            return p_s[0]
        elif fragments is None:
            print("WARN:: Multiple subjects extracted without fragments.")
            return p_s[0]
        f_s = [ps for ps in p_s if any(f in ps for f in fragments)]
        if f_s == []:
            print("WARN:: Multiple subjects extracted with fragments.")
            return p_s[0]
        return f_s[0]

    def get_roots(self, graphs, e_type=None, fragments=None):
        graphs = [g for g in graphs if isinstance(g, Graph)]
        all_graphs = SBOLGraph()
        for g in graphs:
            all_graphs += g
        roots = []
        for entity in all_graphs.get_component_definitions():
            if all_graphs.get_heirachical_instances(entity) == []:
                roots.append(entity)
        return self._fragement_prune(fragments, e_type, roots, all_graphs)

    def get_leafs(self, graphs, e_type=None, fragments=None):
        graphs = [g for g in graphs if isinstance(g, Graph)]
        all_graphs = SBOLGraph()
        for g in graphs:
            all_graphs += g
        leafs = []
        for entity in all_graphs.get_component_definitions():
            if all_graphs.get_components(entity) == []:
                leafs.append(entity)
        return self._fragement_prune(fragments, e_type, leafs, all_graphs)

    def _fragement_prune(self, fragments, e_type, subjects, graph):
        i_subjs = []
        if e_type is not None:
            for root in subjects:
                if self._is_derived(root,graph,e_type):
                    i_subjs.append(root)
        if i_subjs != []:
            subjects = i_subjs
        if fragments is None:
            return subjects
        f_subjects = []
        for root in subjects:
            for p in graph.get_properties(root, None):
                if any(f in p.lower() for f in fragments):
                    f_subjects.append(root)
                    break
        if f_subjects != []:
            return f_subjects
        return subjects


    def _is_derived(self,root,graph,e_type):
        roles = ([(nv_characteristic, physical_entity)] + [(nv_role, r)
                    for r in (graph.get_roles(root) + graph.get_types(root))])
        res = map_to_nv(root,roles,model_roots,model)[2]
        if res == e_type:
            return True
        if model.is_derived(res,e_type):
            return True
        if model.is_derived(e_type,res):
            return True
        return False