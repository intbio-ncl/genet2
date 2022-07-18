from rdflib import URIRef,RDF,OWL

class Identifiers:
    def __init__(self,namespace):
        self.server_namespace = namespace

        self.ontology_code = URIRef( self.server_namespace + "/ontologyCode")
        self.namespace = URIRef( self.server_namespace + "/namespace")
        self.mask = URIRef( self.server_namespace + "/mask")
        self.object_ontology = URIRef( self.server_namespace + "/Ontology")
        self.rdf_type = RDF.type
        self.object_owl = OWL
        self.owl_ontology = URIRef(self.object_owl + "Ontology")
        self.owl_class = URIRef(self.object_owl + "Class")