import os
import re

from rdflib import RDFS
from rdflib import URIRef
from rdflib import BNode
from rdflib import RDF
from rdflib import Graph
from rdflib import OWL

import networkx as nx

from app.graphs.neo_graph.model.identifiers import produce_identifiers

model_fn = os.path.join(os.path.dirname(os.path.realpath(__file__)),"nv_design.xml")
class ModelGraph:
    def __init__(self):
        self.graph = _load_graph()
        self.identifiers = produce_identifiers(self)
        self._generate_labels()
        
    def __len__(self):
        return len(self._graph)

    def __eq__(self, obj):
        if isinstance(obj, self.__class__):
            return nx.is_isomorphic(self._graph, obj._graph)
        if isinstance(obj, nx.MultiDiGraph):
            return nx.is_isomorphic(self._graph, obj)
        return False

    def __iter__(self):
        for n in self._graph.nodes:
            yield n

    @property
    def nodes(self):
        return self._graph.nodes

    @property
    def edges(self):
        return self._graph.edges

    @property
    def graph(self):
        return self._graph

    @graph.setter
    def graph(self, graph):
        self._graph = graph

    def add_node(self, n, data):
        self._graph.add_node(n, **data)

    def add_edge(self, n1, n2, key, **kwargs):
        self._graph.add_edge(n1, n2, key=key, **kwargs)
        
    def get_rdf_type(self, subject):
        rdf_type = self.search((subject, RDF.type, None), lazy=True)
        if rdf_type != []:
            return rdf_type[1]
            
    def get_class_code(self,label):
        if not isinstance(label,list):
            label = [label]
        label = [str(l) for l in label]
        for n,data in self.nodes(data=True):
            if str(data["key"]) in label:
                return n
        raise ValueError(f'{label} is not in graph.')

    def search(self, pattern, lazy=False,label_key="key"):
        matches = []
        s, p, o = pattern
        if not isinstance(s, (list, set, tuple)):
            s = [s]
        if p and not isinstance(p, (list, set, tuple)):
            p = [p]
        if o and not isinstance(o, (list, set, tuple)):
            o = [o]
        for subject in s:
            if subject is not None and subject not in self.nodes:
                subject = self._node_from_attr(subject)
            else:
                subject = [subject]
            for ns in subject:
                for n, v, k in self.edges(ns, keys=True):
                    if not p or k in p:
                        n_data = self.nodes[n]
                        v_data = self.nodes[v]
                        if not o or v_data[label_key] in o or v in o:
                            if lazy:
                                return ([n, n_data], [v, v_data], k)
                            matches.append(([n, n_data], [v, v_data], k))
        return matches

    def get_child_predicate(self):
        return self.identifiers.predicates.hasPart

    def get_classes(self,bnodes=True):
        classes = self.search((None,RDF.type,OWL.Class))
        f_classes = []
        for s,p,o in classes:
            if isinstance(s[1]["key"],BNode):
                if not bnodes:
                    continue
                f_classes.append(s)
            else:
                f_classes.append(s)
        return f_classes
    
    def is_base(self,parent,child):
        def up_search(p,c):
            for cp in self.get_parent_classes(c):
                if cp[0] == parent:
                    return True
                if up_search(cp[0],p):
                    return True
            return False
        return up_search(parent,child)

    def is_derived(self,child,parent):
        def down_search(c,p):
            for cc in self.get_child_classes(p):
                if str(cc[1]["key"]) == str(c):
                    return True
                if down_search(c,cc[0]):
                    return True
            return False

        if not isinstance(parent,(list,tuple,set)):
            parent = [parent]
        if not isinstance(child,list):
            child = [child]
        if self.get_class_code(child) in parent:
            return True

        for ch in child:
            if down_search(ch,parent):
                return True
        return False



    def get_bases(self,class_id):
        bases = []
        def up_search(inner_id):
            for cc in self.get_parent_classes(inner_id):
                bases.append(cc)
                up_search(cc[0])
        up_search(class_id)
        return bases

    def get_derived(self,class_id):
        derived = []
        def down_search(inner_id):
            for cc in self.get_child_classes(inner_id):
                derived.append(cc)
                down_search(cc[0])
        down_search(class_id)
        return derived

    def get_parent_classes(self,class_id):
        return [c[1] for c in self.search((class_id,RDFS.subClassOf,None)) 
                if not isinstance(c[1][1]["key"],BNode)]

    def get_child_classes(self,class_id):
        return [c[0] for c in self.search((None,RDFS.subClassOf,class_id)) 
                if not isinstance(c[1][1]["key"],BNode)]
    
    def get_class_depth(self,class_id):
        def _get_class_depth(c_identifier,depth):
            parent = self.get_parent_classes(c_identifier)
            if parent == []:
                return depth
            depth += 1
            c_identifier = parent[0][0]
            return _get_class_depth(c_identifier,depth)
        return _get_class_depth(class_id,0)
   
    def get_base_class(self):
        bases = []
        for c,data in self.get_classes():
            if isinstance(data["key"], BNode):
                continue
            parents = self.get_parent_classes(c)
            if len(parents) == 0:
                bases.append([c,data])
        return bases

    def get_class_properties(self,class_id):
        properties = []
        def up_search(identifier):
            for q,w,e in self.search((None,None,identifier)):
                if e == RDFS.domain:
                    properties.append(q)
                elif e == RDF.rest or e == OWL.unionOf:                    
                    up_search(q[0])
        
        for n,v,k in self.search((None,RDF.first,class_id)):
            up_search(n[0])
        return properties
    
    def get_default_value(self,subject,predicate):
        res = self.search((subject,predicate,None),True)
        if res == []:
            return None
        else:
            return res[1]

    def get_restrictions_on(self,class_id):
        restrictions = []
        for p,p_data in [c[1] for c in self.search((class_id,RDFS.subClassOf,None)) if isinstance(c[1][1]["key"],BNode)]:
            rdf_type = self.get_rdf_type(p)[1]["key"]
            if rdf_type == OWL.Restriction:
                restrictions.append(p)
        return restrictions

    def get_constraint(self,restriction_id):
        constraints = [OWL.allValuesFrom,
                       OWL.someValuesFrom,
                       OWL.hasValue]
        p = None
        c_p = None
        c_v = None
        for n,v,k in self.search((restriction_id,None,None)):
            if k == OWL.onProperty:
                p = v[1]["key"]
            elif k in constraints:
                c_p = k
                c_v = v[0]
        if p is None or c_p is None or c_v is None:
            raise ValueError(f'{restriction_id} is malformed, no constraint.')
        for n,v,k in self.search((c_v,OWL.members,None)):
            constraint = self._get_operator(v[0])
        return p,constraint

    def get_properties(self):
        return [p[0] for p in self.search((None,RDF.type,OWL.ObjectProperty))]

    def get_domain(self,subject):
        r = self.search((subject,RDFS.domain,None),True)
        if r is not None and r != []:
            r = r[1]
        return r

    def get_range(self,subject):
        r = self.search((subject,RDFS.range,None),True)
        if r is not None and r != []:
            r = r[1]
        return r

    def get_union(self,subject):
        return [r[1] for r in self.search((subject,OWL.unionOf,None))]

    def get_equivalent_classes(self,class_id):
        requirements = []
        # Each equivalent class (Currently, only one for each class.)
        for n,v,e in self.search((class_id,OWL.equivalentClass,None)):
            requirements.append(self.get_requirements(v[0]))
        return requirements

    def get_equivalent_properties(self,property_id):
        return [e[1] for e in self.search((property_id,OWL.equivalentProperty,None))]

    def get_requirements(self,class_id):
        requirements = []
        class_data = self.nodes[class_id]
        if not isinstance(class_data["key"],BNode):
            return [(RDF.type,[class_id,class_data])]
        c_triples = self.search((class_id,None,None))
        # IntersectionOf + UnionOf are still classes so 
        # their type triples is added to direct equivalence (Direct propery check.)
        pruned_triples = []
        for n,v,e in c_triples :
            if [c[0] for c in c_triples].count(n) > 1 and e == RDF.type:
                continue
            if e == RDFS.subClassOf or e == OWL.equivalentClass:
                continue
            pruned_triples.append((n,v,e))

        for n,v,e in pruned_triples:
            if e == OWL.intersectionOf:
                requirements.append((OWL.intersectionOf,self.resolve_intersection(v[0])))
            elif e == OWL.unionOf:
                requirements.append((OWL.unionOf, self.resolve_union(v[0])))
            elif e == RDF.type:
                requirements.append((RDF.type,n))
            else:
                requirements.append((e,n))
        return requirements    
    
    def resolve_intersection(self,identifier):
        return self._get_operator(identifier)

    def resolve_union(self,identifier):
        res = self._get_operator(identifier)
        return res

    def get_restriction(self,r_id):
        vals = [OWL.hasValue,OWL.cardinality,
                OWL.minCardinality,OWL.maxCardinality]

        res = self.search((r_id,None,None))
        r_property = [c[1] for c in res if c[2] == OWL.onProperty][0]
        r_value = [c[1:] for c in res if c[2] in vals]
        assert(len(r_value) == 1)
        return [r_property[1]["key"],r_value[0]]

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

    def _get_operator(self,identifier):
        requirements = []
        r = identifier
        while True:
            res = self.search((r,None,None))
            f = [c[1] for c in res if c[2] == RDF.first]
            r = [c[1] for c in res if c[2] == RDF.rest]
            if f == [] or r == []:
                return requirements
            f,f_data = f[0]
            r,r_data = r[0]
            if isinstance(f_data["key"], BNode):
                f_type = self.get_rdf_type(f)[1]["key"]
                if f_type == OWL.Restriction:
                    requirements.append(self.get_restriction(f))
                elif f_type == OWL.Class:
                    requirements += self.get_requirements(f)
                else:
                    raise ValueError("Wut")
            elif f in [c[0] for c in self.get_classes(False)]:
                requirements.append((RDF.type,[f,f_data]))
            if r_data["key"] == RDF.nil:
                break
        return requirements

    def _generate_labels(self):
        for node,data in self.nodes(data=True):
            if "display_name" not in data.keys():
                identity = data["key"]
                if isinstance(identity,URIRef):
                    name = (self.identifiers.namespaces.get_code(identity) + 
                            self._get_name(identity))
                else:
                    name = str(identity)
                self.nodes[node]["display_name"] = name
        for n,v,k,e in self.edges(keys=True,data=True):
            if "display_name" not in e.keys():
                e["display_name"] = self._get_name(k)

def _isfloat(x):
    try:
        float(x)
        return True
    except ValueError:
        return False


def _load_graph():

    g = Graph()
    g.load(model_fn)
    nx_graph = nx.MultiDiGraph()
    node_count = 1
    node_map = {}
    def _add_node(entity,node_count):
        if entity in node_map.keys():
            n_key = node_map[entity]
        else:
            n_key = node_count
            node_map[entity] = n_key
            node_count += 1
        nx_graph.add_node(n_key, key=entity)
        return n_key,node_count

    for s,p,o in g.triples((None,None,None)):
        n,node_count = _add_node(s,node_count)
        v,node_count = _add_node(o,node_count)
        nx_graph.add_edge(n,v,key=p,weight=1)

    return nx_graph