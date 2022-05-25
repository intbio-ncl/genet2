from rdflib import RDF

from app.graphs.neo_graph.graph import Graph
from app.graphs.neo_graph.gds.project import ProjectBuilder
from app.graphs.neo_graph.gds.procedures import Procedures
from app.graphs.graph_objects.node import Node

class NVGraph(Graph):
    def __init__(self):
        super().__init__()
        self.ids = self.model.identifiers
        self.procedure = Procedures(self)
        self.project = ProjectBuilder(self)


    def get_entities(self):
        derived = ([self.ids.objects.entity] + 
                   [n[1]["key"] for n in self.model.get_derived(self.ids.objects.physical_entity)])
        return self.node_query(derived)

    def get_physical_entities(self):
        derived = ([self.ids.objects.physical_entity] + 
                   [n[1]["key"] for n in self.model.get_derived(self.ids.objects.physical_entity)])
        return self.node_query(derived)

    def get_conceptual_entities(self):
        derived = ([self.ids.objects.conceptual_entity] + 
                   [n[1]["key"] for n in self.model.get_derived(self.ids.objects.conceptual_entity)])
        return self.node_query(derived)

    def get_interactions(self):
        derived = ([self.ids.objects.interaction] + 
                   [n[1]["key"] for n in self.model.get_derived(self.ids.objects.interaction)])
        return self.node_query(derived)

    def get_children(self,parent):
        cp = self.model.get_child_predicate()
        return self.edge_query(n=parent,e=cp)

    def get_consists_of(self,interaction):
        return self.edge_query(n=interaction,e=self.ids.predicates.consists_of)
    
    def derive_consistsOf(self,item):

        elements = []
        next_id = item
        while True:
            res = self.edge_query(n=next_id)
            f = [c.v for c in res if str(RDF.first) in c.get_type()]
            r = [c for c in res if str(RDF.rest) in c.get_type()]
            if len(f) != 1 or len(r) != 1:
                raise ValueError(f'{item} is a malformed list.')
            elements.append(f[0])
            r = r[0]
            if str(RDF.nil) in r.v.get_labels():
                break
            next_id = r.v
        return elements

    def labels_to_node(self, labels):
        return Node(*self._derive_key_type(labels))

    def _derive_key_type(self, labels):
        assert(len(labels) == 2)
        labels = list(labels)
        if "None" in labels:
            return [l for l in labels if l != "None"][0], "None"
        res = self.model.are_classes(labels)
        if res[0]:
            assert(not res[1])
            return labels[::-1]
        if res[1]:
            assert(not res[0])
            return labels