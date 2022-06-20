from app.graph.truth_graph.truth_graph import TruthGraph
from app.graph.design_graph.design_graph import DesignGraph
from  app.graph.neo4j_interface.interface import Neo4jInterface
from  app.graph.design_graph.converter.handler import file_convert

class WorldGraph:
    def __init__(self):
        self.driver = Neo4jInterface()
        self.truth = TruthGraph(self.driver)

    def add_design(self,fn,graph_name,mode="merge"):
        file_convert(self.driver,fn,mode,graph_name)
        return DesignGraph(self.driver,graph_name)

    def get_design(self,graph_name,predicate="ALL"):
        if graph_name == "*":
            graph_name = self.get_design_names()
        return DesignGraph(self.driver,graph_name,predicate=predicate)
    
    def get_design_names(self):
        gns = self.driver.node_property("graph_name",distinct=True)
        try:
            gns.remove(self.truth.name)
        except ValueError:
            pass
        return list(set(gns))

    def remove_design(self,graph):
        if isinstance(graph,DesignGraph):
            graph = graph.name
        return self.driver.remove_graph(graph)
        