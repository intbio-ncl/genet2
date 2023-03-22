from app.graph.truth_graph.truth_graph import TruthGraph
from app.graph.design_graph.design_graph import DesignGraph
from app.graph.neo4j_interface.interface import Neo4jInterface
reserved_names = ["truth_graph"]
class WorldGraph:
    def __init__(self):
        self.driver = Neo4jInterface(reserved_names=reserved_names)
        self.truth = TruthGraph(reserved_names[0],self.driver)

    def new_design(self,graph_name):
        if graph_name in self.get_design_names():
            raise ValueError(f'{graph_name} is already in use.')
        return DesignGraph(self.driver,graph_name)

    def get_design(self,graph_name):
        if graph_name == "*":
            graph_name = self.get_design_names()
        if graph_name == self.truth.name:
            return self.truth
        return DesignGraph(self.driver,graph_name)
    
    def get_design_names(self):
        gns = self.driver.node_property("graph_name",distinct=True)
        gns = list(set(gns) - set(reserved_names))
        return list(set(gns))

    def remove_design(self,graph):
        if isinstance(graph,DesignGraph):
            graph = graph.name
        return self.driver.remove_graph(graph)

    def export_design(self,graphs,dir="",originals=None):
        out_locs = []
        if not isinstance(graphs,list):
            graphs = [graphs]
        if originals is not None and not isinstance(originals,list):
            originals = [originals]
        for index,graph in enumerate(graphs):
            if originals is not None:
                original = originals[index]
            else:
                original = None
            d = self.get_design(graph)
            out_locs.append(d.export(dir=dir,original=original))
        return out_locs
    

    def get_truth(self,edge,threshold=None):
        return self.truth.get(edge,threshold=threshold)

    def drop_truth_graph(self):
        self.truth.drop()

        
    def get_projected_names(self):
        return self.driver.project.names()