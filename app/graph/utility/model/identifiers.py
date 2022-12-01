import re

from rdflib import RDF,OWL,RDFS
from rdflib.term import BNode, URIRef
from  app.graph.utility.model.nv_graph_build.identifiers import identifiers as nv_ids

nv_namespace = URIRef("http://www.nv_ontology.org/")
class KnowledgeGraphIdentifiers:
    def __init__(self):
        self.objects = Objects()
        self.predicates = Predicates()
        self.roles = Roles()
        self.namespaces = Namespaces()
        self.external = External()

class Namespaces:
    def __init__(self):
        identifiers = URIRef('http://identifiers.org/')
        self.nv = nv_namespace
        self.so = URIRef(identifiers + 'so/SO:')
        self.sbo = URIRef(identifiers + 'biomodels.sbo/SBO:') 
        self.i_edam = URIRef(identifiers + 'edam/')
        self.go = URIRef(identifiers + "go/GO:")
        self.chebi = URIRef(identifiers + "chebi/CHEBI:")
        self.biopax = URIRef('http://www.biopax.org/release/biopax-level3.owl#')
        self.dc = URIRef('http://purl.org/dc/terms/')
        self.edam = URIRef('http://edamontology.org/format')
        self.prov = URIRef('http://www.w3.org/ns/prov#')


    def get_code(self,identity):
        for code,identifier in vars(self).items():
            if identifier in identity:
                return code + ":"
        return ""

class Predicates:
    def __init__(self):
        self.rdf_type = RDF.type
    
    def __iter__(self):
        for i in dir(self):
            attr = getattr(self,i)
            if isinstance(attr,(URIRef)):
                yield attr

class Objects:
    def __init__(self):
        pass

    def __iter__(self):
        for i in dir(self):
            attr = getattr(self,i)
            if isinstance(attr,(URIRef)):
                yield attr

class Roles:
    def __init__(self):
        pass
    
    def __iter__(self):
        for i in dir(self):
            attr = getattr(self,i)
            if isinstance(attr,(URIRef)):
                yield attr

class External:
    def __init__(self):
        self.type = RDF.type
        self.confidence = URIRef("http://purl.obolibrary.org/obo/NCIT_C49020")
        self.synonym = URIRef("http://purl.obolibrary.org/obo/NCIT_C52469")
        self.similar_to = URIRef("http://semanticscience.org/resource/CHEMINF_000481")
        self.description = URIRef("http://purl.org/dc/terms/description")



def produce_identifiers(graph):
    bl_namespaces = [str(OWL),str(RDF),str(RDFS)]
    known_namespaces = [str(OWL),str(RDF),str(RDFS)]
    for k,v in nv_ids.roles.__dict__.items():
        setattr(Roles, k, v)
    for n,v,e in graph.search((None,None,None)):
        n,n_data = n
        v,v_data = v
        n_key = n_data["key"]
        v_key = v_data["key"]

        # Adds Classes.
        if e == RDF.type and v_key == OWL.Class and not isinstance(n_key, BNode):
            _apply_var_variants(Objects,n_key)
        # Adds external ontology terms
        if e == OWL.hasValue:
            _apply_var_variants(Roles,v_key)
        if nv_namespace in e:
            _apply_var_variants(Objects,v_key)
        
        # Adds object properties
        if v_key == OWL.ObjectProperty:
            _apply_var_variants(Predicates,n_key)  

        if any(ext in e for ext in bl_namespaces):
            continue
        if e in [getattr(Predicates,i) for i in dir(Predicates)]:
            continue
        # Adds any predicates that aren't attached to a object
        # (Property of properties)
        _apply_var_variants(Predicates,e)       
        _extract_namespaces((n_key,v_data,e),known_namespaces)
    
    return KnowledgeGraphIdentifiers()


def _extract_namespaces(triple,known_namespaces):
    for code,ns in vars(Namespaces()).items():
        if "__" in ns:
            continue
        known_namespaces.append(ns)
    known_namespaces = list(set(known_namespaces))
    for t in triple:
        if not isinstance(t,URIRef):
            continue
        if any(ns in t for ns in known_namespaces):
            continue
        namespace = t[0:len(t) - len(_get_name(t))]
        nv_code = _split(namespace)[-2]
        nv_code = re.split('\W+', nv_code)[0]
        setattr(Namespaces, nv_code, URIRef(namespace))


def _apply_var_variants(class_name,key):
    if not isinstance(key,URIRef):
        return
    var_name = _get_name(key)
    setattr(class_name, var_name, key)
    lower_var_name = var_name.lower()
    setattr(class_name, lower_var_name, key)
    lower_space_list = []
    for index,l in enumerate(var_name):
        if l.islower():
            lower_space_list.append(l)
        elif index == 0:
            lower_space_list.append(l.lower())
        else:
            lower_space_list.append("_" + l.lower())
    lower_space_name = "".join(lower_space_list)
    setattr(class_name, lower_space_name, key)

def _get_name(subject):
    split_subject = _split(subject)
    if len(split_subject[-1]) == 1 and split_subject[-1].isdigit():
        return split_subject[-2]
    else:
        return split_subject[-1]

def _split(uri):
    return re.split('#|\/|:', uri)

