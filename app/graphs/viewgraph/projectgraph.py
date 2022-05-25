import networkx as nx
from app.graphs.viewgraph.viewgraph import ViewGraph

class ProjectGraph(ViewGraph):
    def __init__(self, graph=None):
        super().__init__(graph)
        self._graph = graph if graph else nx.MultiDiGraph()
        self._project = None

    def name(self):
        return self._project.name()
        
    def set_project(self,graph):
        self._project = graph

    def get_metadata(self):
        schema = self._project._graph_info(["schema"])
        nodes = schema["nodes"]
        edges = schema["relationships"]
        return [{"name" : self._project.name(),
                "node_count" : self._project.node_count(),
                "relationship_count" : self._project.relationship_count(),
                "memory_usage" : self._project.memory_usage(),
                "node-schema" : str(nodes),
                "edge-schema" : str(edges)}]
