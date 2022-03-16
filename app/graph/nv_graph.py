from app.graph.graph import Graph
from rdflib import RDF

class NVGraph(Graph):
    def __init__(self):
        super().__init__()
        self.ids = self._model.identifiers

    def get_objects(self):
        return self.edge_query(e=self.ids.predicates.rdf_type)

    def get_object_type(self,obj):
        res = self.edge_query(n=obj,e=self.ids.predicates.rdf_type)
        if res != []:
            return res[0].v

    def get_physical_entities(self):
        derived = ([self.ids.objects.physical_entity] + 
                   [n[1]["key"] for n in self._model.get_derived(self.ids.objects.physical_entity)])
        return self.edge_query(e=self.ids.predicates.rdf_type,v=derived)

    def get_conceptual_entities(self):
        derived = ([self.ids.objects.conceptual_entity] + 
                   [n[1]["key"] for n in self._model.get_derived(self.ids.objects.conceptual_entity)])
        return self.edge_query(e=self.ids.predicates.rdf_type,v=derived)

    def get_interactions(self):
        derived = ([self.ids.objects.interaction] + 
                   [n[1]["key"] for n in self._model.get_derived(self.ids.objects.interaction)])
        return self.edge_query(e=self.ids.predicates.rdf_type,v=derived)

    def get_children(self,parent):
        cp = self._model.get_child_predicate()
        return self.edge_query(n=parent,e=cp)

    def get_consists_of(self,interaction):
        return self.edge_query(n=interaction,e=self.ids.predicates.consists_of)
    
    def derive_consistsOf(self,item):
        elements = []
        next_id = item
        while True:
            res = self.edge_query(n=next_id)
            f = [c.v for c in res if str(RDF.first) in c.get_labels()]
            r = [c for c in res if str(RDF.rest) in c.get_labels()]
            if len(f) != 1 or len(r) != 1:
                raise ValueError(f'{item} is a malformed list.')
            elements.append(f[0])
            r = r[0]
            if str(RDF.nil) in r.v.get_labels():
                break
            next_id = r.v
        return elements