from app.visualiser.builder.builders.abstract_view import AbstractViewBuilder
from app.visualiser.viewgraph.projectgraph import ProjectGraph
from app.graph.utility.graph_objects.edge import Edge
import re
import networkx as nx
from urllib.parse import urlparse

class ProjectionViewBuilder(AbstractViewBuilder):
    def __init__(self,graph):
        super().__init__(graph)

    def build(self, graph_name,datatable=False):
        p_graph = self._graph.get_project_graph(graph_name)
        graph = self._build_projection_graph(p_graph)
        
        if not datatable:
            return graph
        datatable = []
        for edge in graph.edges():
            row = {"n" : str(edge.n.name),
                   "v" : str(edge.v.name),
                   "e" : str(edge.name)}
            datatable.append(row)
        return graph, datatable

    def get_edge_types(self):
        pass
    
    def get_node_types(self):
        pass

    def transform(self,edges):
        return []
        
    def _build_projection_graph(self, graph):
        config = graph._graph_info(["configuration"])
        if "relationshipQuery" in config:
            qry = config["relationshipQuery"]
            qry = re.split("return", qry, flags=re.IGNORECASE)[0]
            node1, node2 = re.findall(r"\(([A-Za-z0-9_]+)\)", qry)
            edge_c = re.search(r"\[(.+)\]", qry)
            edge_c = edge_c[1].split(":")[0]
            qry += f"return {node1},{node2},{edge_c}"
            elements = [n[edge_c] for n in self._graph.driver.run_query(qry)]
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
            elements = self._graph.edges(n = nl, v = nl, e = el)
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
        sg = self._subgraph(elements, project_graph=graph)
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
                            n = self._graph.nodes(name=parts[-2])
                            assert(len(n) == 1)
                            n = n[0]
                            v = self._graph.nodes(name=parts[-1])
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
                            n = self._graph.nodes(name=parts[-2])
                            assert(len(n) == 1)
                            n = n[0]
                            v = self._graph.nodes(name=parts[-1])
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

    def _subgraph(self, edges=[], nodes=[],new_graph=None,project_graph=None):
        g = ProjectGraph(super()._subgraph(edges,nodes,new_graph))
        g.set_project(project_graph)
        return g

    def _try_remove_edge(self, edge, graph):
        try:
            graph.remove_edge(edge)
        except nx.exception.NetworkXError:
            pass

class ViewBuilder(AbstractViewBuilder):
    def __init__(self, graph):
        super().__init__(graph)

    def none(self):
        return self._subgraph([])
        
