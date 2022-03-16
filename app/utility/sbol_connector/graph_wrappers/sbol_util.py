from app.utility.sbol_connector.sbol_identifiers import identifiers
from app.utility.sbol_connector.graph_wrappers.rdf import RDFGraphWrapper

class SBOLGraphUtil:
    def __init__(self,graph):
        self.graph = RDFGraphWrapper(graph)

    def __iter__(self):
        for x in self.graph:
            yield x

    def __len__(self):
        return len(self.graph)

    def sub_graph(self,pattern):
        triples = self.search(pattern)
        return self.graph.sub_graph(triples)

    # ----- RDF-Type searches ------
    def get_instances(self,object_type=None):
        return self.search((None,identifiers.predicates.rdf_type,object_type))

    def get_rdf_type(self,subject):
        return self.search((subject,identifiers.predicates.rdf_type,None),lazy=True)

    # ----- Instance searches ----
    def get_cd_instances(self,component_definition):
        return self.search((None,identifiers.predicates.definition,component_definition))

    def get_definition(self,sub_component):
        return self.search((sub_component,identifiers.predicates.definition,None),lazy=True)
        
    def get_definitions(self):
        return self.search((None,identifiers.predicates.definition,None))

    # ----- Parent / Child Searches -----
    # - Parent Searches
    def get_parent(self,child,predicate):
        if predicate == identifiers.predicates.component:
            for s,p,o in self.search((None,predicate,child)):
                if self.get_rdf_type(s)[2] == identifiers.objects.component_definition:
                    return s,p,o
        return self.search((None,predicate,child),lazy=True)

    # - Child Searches -
    def get_children(self,parent,predicate):
        return self.search((parent,predicate,None))

    # ----- Property Searches -----
    def get_subject(self,predicate,t_object):
        return self.search((None,predicate,t_object))
    
    def get_object(self,subject,predicate,single=False):
        return self.search((subject,predicate,None),lazy=single)

    def get_type(self,subject):
        return self.search((subject,identifiers.predicates.type,None),lazy=True)
        
    def get_types(self,subject):
        return self.search((subject,identifiers.predicates.type,None))

    def get_roles(self,subject):
        roles = self.search((subject,identifiers.predicates.role,None))
        return roles
    
    def search(self,pattern,lazy=False):
        return self.graph.search(pattern,lazy=lazy)

    def add_graph(self,graph):
        if isinstance(graph,SBOLGraphUtil):
            return self.graph.add_graph(graph.graph)
        return self.graph.add_graph(graph)

    def add(self,triples):
        # Need to add the triples to the intermediate sub_graphs also.
        if not isinstance(triples,list):
            triples = [triples]
        for s,p,o in triples:
            try:
                self.sub_graphs[p].add(triples)
            except KeyError:
                continue

        return self.graph.add(triples)

    def remove(self,triples):
        return self.graph.remove(triples)

    def save(self,filename,format="xml"):
        return self.graph.save(filename,format)

    def serialise(self,serialisation = "rdfxml"):
        return self.graph.serialise(serialisation)



