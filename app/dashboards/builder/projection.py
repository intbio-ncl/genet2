from urllib.parse import urlparse
import re
import inspect
import networkx as nx
from app.graphs.viewgraph.projectgraph import ProjectGraph
from app.dashboards.builder.abstract import AbstractBuilder
from app.dashboards.builder.builders.projection.view import ViewBuilder
from app.dashboards.builder.builders.projection.mode import ModeBuilder
from app.graphs.graph_objects.edge import Edge


class ProjectionBuilder(AbstractBuilder):
    def __init__(self, graph):
        super().__init__(graph)
        self.view = ProjectGraph()
        self._view_h = ViewBuilder(self)
        self._mode_h = ModeBuilder(self)

    def set_no_view(self):
        self.view = self._view_h.none()

    def set_projection_view(self, graph_name, datatable=False):
        if datatable:
            view, datatabe = self._view_h.projection(graph_name, datatable)
            self.view = view
            return datatabe
        self.view = self._view_h.projection(graph_name, datatable)

    def run_query(self, qry_str):
        return self._graph.run_query(qry_str)

    def get_edges(self, node):
        return self._graph.edge_query(n=node)

    def edge_query(self, n=None, v=None, e=None, directed=False):
        return self._graph.edge_query(n, v, e, directed=directed)

    def node_query(self, n):
        return self._graph.node_query(n)

    def get_project_preset_names(self):
        return self._graph.project.get_presets()

    def get_project_graph_names(self):
        return self._graph.project.get_projected_names()

    def get_project_graph(self, graph_name):
        return self._graph.project.get_graph(graph_name)

    def project_graph(self, name, nodes, edges, n_props, e_props, **kwargs):
        return self._graph.project.project(name, nodes, edges,
                                           nodeProperties=n_props, relationshipProperties=e_props, **kwargs)

    def project_preset(self, name, preset, **kwargs):
        return self._graph.project.preset(name, preset, **kwargs)

    def get_node_labels(self):
        return self._graph.get_node_labels()

    def get_edge_labels(self):
        return self._graph.get_edge_labels()

    def get_node_properties(self):
        return self._graph.get_node_properties()

    def get_edge_properties(self):
        return self._graph.get_edge_properties()

    def get_graph_metadata(self):
        return self.view.get_metadata()

    def get_project_info(self):
        nodes = []
        gn = self.view.name()
        pr = self._graph.procedure.centrality.page_rank(gn)
        bc = self._graph.procedure.centrality.betweenness(gn)
        dc = self._graph.procedure.centrality.degree(gn)
        cc = self._graph.procedure.centrality.closeness(gn)
        louv = self._graph.procedure.community_detection.louvain(gn)
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
                  "mode": self._graph.procedure.modes}

        struct = {}
        for name, obj in self._graph.procedure.__dict__.items():
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
                   "interaction_ppi": {"direction": ["DIRECTED", "UNDIRECTED"], "type": ["monopartite", "bipartite"]},
                   "interaction_genetic": {"direction": ["DIRECTED", "UNDIRECTED"], "type": ["monopartite", "bipartite"]}}
        if preset not in presets:
            return []
        return presets[preset]

    def get_parameter_types(self, params):
        nodes = [n.get_key() for n in self.view.nodes()]
        mapper = {"node": nodes,
                  "source": nodes,
                  "dest": nodes,
                  "mode": self._graph.procedure.modes}
        types = []
        for p in params:
            if p in mapper:
                types.append(mapper[p])
            else:
                types.append(None)
        return types

    def run_procedure(self, module, name, params):
        ordered_params = [self.view.name()]
        module = getattr(self._graph.procedure, module)
        func = getattr(module, name)
        for arg in inspect.getfullargspec(func).args[2:]:
            ordered_params.append(params[arg])
        return func(*ordered_params)

    def build_projection_graph(self, graph):
        config = graph._graph_info(["configuration"])
        if "relationshipQuery" in config:
            qry = config["relationshipQuery"]
            qry = re.split("return", qry, flags=re.IGNORECASE)[0]
            node1, node2 = re.findall(r"\(([A-Za-z0-9_]+)\)", qry)
            edge_c = re.search(r"\[(.+)\]", qry)
            edge_c = edge_c[1].split(":")[0]
            qry += f"return {node1},{node2},{edge_c}"
            elements = [n[edge_c] for n in self.run_query(qry)]
        else:
            nodes = config["nodeProjection"]
            edges = config["relationshipProjection"]
            if "__ALL__" in nodes.keys():
                nl = None
            else:
                nl = list(nodes.keys())

            if "__ALL__" in edges.keys():
                el = None
            else:
                el = list(edges.keys())
            elements = self.edge_query(nl, nl, el, directed=True)
            for index in range(0, len(elements)):
                element = elements[index]
                element_t = str(element.get_type())
                orientation = None
                if "__ALL__" in edges:
                    orientation = edges["__ALL__"]["orientation"]
                if element_t in edges:
                    orientation = edges[element_t]["orientation"]
                if orientation == "REVERSE":
                    n = element.n
                    v = element.v
                    element.n = v
                    element.v = n
                elif orientation == "UNDIRECTED":
                    inverse = Edge(element.v,element.n,element.get_type(),**element.get_properties())
                    if inverse not in elements:
                        elements.append(inverse)
        sg = self.sub_graph(elements, graph)
        if "relationshipFilter" in config:
            # Find the filter in the graph
            e_flter = re.findall(r"`(.+?)`", config["relationshipFilter"])
            nflter = re.findall(r"`(.+?)`", config["nodeFilter"])
            edges = [*sg.edges()]
            for edge in edges:
                if edge.get_type() in e_flter:
                    continue
                elif edge.v.get_type() in e_flter:

                    for edge1 in edges:
                        if edge.v == edge1.n:
                            ne = Edge(edge.n, edge1.v, edge.v.get_type(),
                                      **edge.v.get_properties())
                            if sg.has_edge(ne) or edge.n == edge1.v:
                                continue
                            sg.add_edge(ne)
                            self._try_remove_edge(edge1, sg)
                elif edge.n.get_type() in e_flter:
                    for edge1 in edges:
                        if edge.n == edge1.v:
                            ne = Edge(edge1.n, edge.v, edge.n.get_type(),
                                      **edge.n.get_properties())
                            if sg.has_edge(ne) or edge1.n == edge.v:
                                continue
                            sg.add_edge(ne)
                            self._try_remove_edge(edge1, sg)
                else:
                    # https://github.com/neo4j/graph-data-science/issues/201
                    n_name = self._get_name(edge.n.get_key())
                    v_name = self._get_name(edge.v.get_key())
                    for e_flt in e_flter:
                        if edge.v.get_type() in e_flt and n_name in e_flt:
                            url = urlparse(e_flt)
                            parts = self._split(url.path)
                            n = self._graph.node_query(name=parts[-2])
                            assert(len(n) == 1)
                            n = n[0]
                            v = self._graph.node_query(name=parts[-1])
                            assert(len(v) == 1)
                            v = v[0]
                            e = f'{url.scheme}://{url.netloc}/{parts[-3]}'
                            ne = Edge(n, v, e, name=parts[-3])
                            if not sg.has_edge(ne):
                                sg.add_edge(ne)
                            # break
                        elif edge.n.get_type() in e_flt and v_name in e_flt:
                            url = urlparse(e_flt)
                            parts = self._split(url.path)
                            n = self._graph.node_query(name=parts[-2])
                            assert(len(n) == 1)
                            n = n[0]
                            v = self._graph.node_query(name=parts[-1])
                            assert(len(v) == 1)
                            v = v[0]
                            e = f'{url.scheme}://{url.netloc}/{parts[-3]}'
                            ne = Edge(n, v, e, name=parts[-3])
                            if not sg.has_edge(ne):
                                sg.add_edge(ne)
                            # break
                self._try_remove_edge(edge, sg)
        sg.remove_isolated_nodes()
        return sg

    def sub_graph(self, edges, project_graph=None):
        g = super().sub_graph(edges)
        g.set_project(project_graph)
        return g

    def _try_remove_edge(self, edge, graph):
        try:
            graph.remove_edge(edge)
        except nx.exception.NetworkXError:
            pass

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
