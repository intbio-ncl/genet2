import re
import inspect
import networkx as nx
from app.visualiser.viewgraph.projectgraph import ProjectGraph
from app.visualiser.builder.abstract import AbstractBuilder
from app.visualiser.builder.builders.projection.none import NoneViewBuilder
from app.visualiser.builder.builders.projection.projection import ProjectionViewBuilder

class ProjectionBuilder(AbstractBuilder):
    def __init__(self,graph):
        super().__init__(graph)
        self._dg = self._graph.get_design(None)
        self._view_builder = NoneViewBuilder(self._dg)
        self.projection_name = None

    def build(self,create_datatable=True):
        if create_datatable:
            view,dt = self._view_builder.build(self.projection_name,create_datatable)
            self.view=view
            return dt
        self.view = self._view_builder.build(self.projection_name,create_datatable)

    def set_no_view(self):
        self._view_builder = NoneViewBuilder(self._dg)

    def set_projection_view(self):
        self._view_builder = ProjectionViewBuilder(self._dg)

    def set_projection_graph(self,name):
        self.projection_name = name

    def get_design_names(self):
        return self._graph.get_design_names()

    def set_design_names(self,names):
        self.set_design(self._graph.get_design(names))
    
    def set_design(self,design):
        self._dg = design
        self._view_builder.set_graph(design)

    def run_cypher(self, qry_str):
        return self._dg.driver.run_query(qry_str)

    def get_edges(self, node):
        return self._graph.edge_query(n=node)

    def edge_query(self, n=None, v=None, e=None, directed=False):
        return self._graph.edge_query(n, v, e, directed=directed)

    def node_query(self, n):
        return self._graph.node_query(n)

    def project_graph(self, name, nodes, edges, n_props, e_props, **kwargs):
        return self._dg.driver.project.project(name, nodes, edges,nodeProperties=n_props, relationshipProperties=e_props, **kwargs)

    def project_preset(self, name, preset, **kwargs):
        f = getattr(self._dg.project, preset)
        return f(name,**kwargs)

    def get_project_preset_names(self):
        return self._dg.get_project_preset_names()

    def get_project_graph_names(self):
        return self._dg.get_projected_names()

    def get_node_labels(self):
        labels = []
        for node in self._dg.nodes():
            labels += [node.get_key(),node.get_type()]
        return list(set(labels))

    def get_edge_labels(self):
        return [e.get_type() for e in self._dg.edges()]

    def get_node_properties(self):
        return [node.get_properties() for node in self._dg.nodes()]

    def get_edge_properties(self):
        return [edge.get_properties() for edge in self._dg.edges()]

    def get_graph_metadata(self):
        return self.view.get_metadata()

    def get_project_info(self):
        nodes = []
        gn = self.view.name()
        pr = self._graph.driver.procedures.centrality.page_rank(gn)
        bc = self._graph.driver.procedures.centrality.betweenness(gn)
        dc = self._graph.driver.procedures.centrality.degree(gn)
        cc = self._graph.driver.procedures.centrality.closeness(gn)
        louv = self._graph.driver.procedures.community_detection.louvain(gn)
        for index, node in enumerate(self.v_nodes()):
            struct = {"Node": str(node),
                      "Page Rank": pr[index]["score"],
                      "Betweeness Centrality": bc[index]["score"],
                      "Degree Centrality": dc[index]["score"],
                      "Closeness Centrality": cc[index]["score"],
                      "Louvain (Clustering)": louv[index]["communityId"]}
            nodes.append(struct)
        return nodes

    def get_procedures_info(self):
        nodes = [n.get_key() for n in self.view.nodes()]
        mapper = {"node": nodes,
                  "source": nodes,
                  "dest": nodes,
                  "mode": self._graph.driver.procedures.modes}

        struct = {}
        for name, obj in self._graph.driver.procedures.__dict__.items():
            funcs = {}
            for method_name in dir(obj):
                method = getattr(obj, method_name)
                if (callable(method) and not method_name.startswith("_")):
                    params = {}
                    for p in inspect.getfullargspec(method).args[2:]:
                        if p in mapper:
                            params[p] = mapper[p]
                        else:
                            params[p] = None
                    funcs[method_name] = params
            struct[name] = funcs
        return struct

    def get_project_preset_parameters(self, preset):
        presets = {"hierarchy": {"direction": ["NATURAL", "REVERSE", "UNDIRECTED"]},
                   "interaction": {"direction": ["NATURAL", "DIRECTED", "UNDIRECTED"], "type": ["monopartite", "bipartite"]},
                   "interaction_ppi": {"direction": ["DIRECTED", "UNDIRECTED"]},
                   "interaction_genetic": {"direction": ["DIRECTED", "UNDIRECTED"]}}
        if preset not in presets:
            return []
        return presets[preset]

    def get_parameter_types(self, params):
        nodes = [n.get_key() for n in self.view.nodes()]
        mapper = {"node": nodes,
                  "source": nodes,
                  "dest": nodes,
                  "mode": self._graph.driver.procedures.modes}
        types = []
        for p in params:
            if p in mapper:
                types.append(mapper[p])
            else:
                types.append(None)
        return types

    def run_procedure(self, module, name, params):
        ordered_params = [self.view.name()]
        module = getattr(self._graph.driver.procedures, module)
        func = getattr(module, name)
        for arg in inspect.getfullargspec(func).args[2:]:
            ordered_params.append(params[arg])
        return func(*ordered_params)

    def _get_name(self, subject):
        split_subject = self._split(subject)
        if len(split_subject[-1]) == 1 and split_subject[-1].isdigit():
            return split_subject[-2]
        elif len(split_subject[-1]) == 3 and _isfloat(split_subject[-1]):
            return split_subject[-2]
        else:
            return split_subject[-1]

    def _split(self, uri):
        return re.split('#|\/|:', uri)


def _isfloat(x):
    try:
        float(x)
        return True
    except ValueError:
        return False
