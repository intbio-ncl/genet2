from rdflib import URIRef,Literal

class StaticOntologyData:
    class Ontology:
        def __init__(self,server_uri,ontology_code,namespace,standard_mask):
            self.server_uri = URIRef(server_uri)
            self.ontology_code = Literal(ontology_code)
            self.namespace = URIRef(namespace)
            self.standard_mask = URIRef(standard_mask)

    def __init__(self):
        self.ontologies = [self.Ontology("http://ontology_server/GO", 
                                         "GO",
                                         "http://purl.obolibrary.org/obo",
                                         "http://identifiers.org/go"),

                           self.Ontology("http://ontology_server/SBO",
                                         "SBO",
                                         "http://biomodels.net/SBO",
                                         "http://identifiers.org/biomodels.sbo"),

                           self.Ontology("http://ontology_server/biopax-level3",
                                         "biopax-level3",
                                         "http://www.biopax.org/release/biopax-level3.owl",
                                         "http://www.biopax.org/release/biopax-level3.owl"),

                           self.Ontology("http://ontology_server/EDAM",
                                         "EDAM",
                                         "http://edamontology.org",
                                         "http://identifiers.org/edam"),

                           self.Ontology("http://ontology_server/SO",
                                         "SO",
                                         "http://purl.obolibrary.org/obo",
                                         "http://identifiers.org/so"),

                           self.Ontology("http://ontology_server/CHEBI",
                                         "CHEBI",
                                         "http://purl.obolibrary.org/obo",
                                         "http://identifiers.org/chebi")
                            ]

    def __iter__(self):
        for ontology in self.ontologies:
            yield ontology