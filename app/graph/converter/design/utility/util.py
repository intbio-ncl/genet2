from rdflib import Graph,RDF
from app.graph.converter.design.utility.identifiers import identifiers


rdf_type = RDF.type
class SBOLGraphUtil:
    def __init__(self,graph):
        self.graph = Graph()
        self.graph.load(graph)
        self.rdf_type = identifiers.predicates.rdf_type
        self.definition = identifiers.predicates.definition
        self.type = identifiers.predicates.type
        self.role = identifiers.predicates.role
             
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
        return self.search((None,rdf_type,object_type))

    def get_rdf_type(self,subject):
        return self.search((subject,rdf_type,None),lazy=True)

    # ----- Instance searches ----
    def get_cd_instances(self,component_definition):
        return self.search((None,self.definition,component_definition))

    def get_definition(self,sub_component):
        return self.search((sub_component,self.definition,None),lazy=True)
        

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
        return self.search((subject,self.type,None),lazy=True)
        
    def get_types(self,subject):
        return self.search((subject,self.type,None))

    def get_roles(self,subject):
        roles = self.search((subject,self.role,None))
        return roles
    
    def search(self,pattern,lazy=False):
        if any([isinstance(p,list) for p in pattern]):
            results = []
            sp,pp,op = pattern
            for s,p,o in self.graph:
                if sp and s not in sp and s != sp:
                    continue
                if pp and p not in pp and p != pp:
                    continue
                if op and o not in op and o != op:
                    continue
                if lazy:
                    return (s,p,o)
                results.append((s,p,o))
            return results
        if lazy:
            for res in self.graph.triples(pattern):
                return res
            return None
        else:
            results = []
            for res in self.graph.triples(pattern):
                results.append(res)
            return results




