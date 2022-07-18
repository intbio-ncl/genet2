import os
import atexit

from rdflib import Graph,URIRef,Literal

from graph.knowledge.data_miner.ontology.server_interface.utility.identifiers import Identifiers
from graph.knowledge.data_miner.ontology.server_interface.utility.static_data import StaticOntologyData

ontology_graph = os.path.join(os.path.dirname(os.path.realpath(__file__)),"ontologies.xml")
class OntologyGraph:
    def __init__(self,ontology_server,namespace):
        self.identifiers = Identifiers(namespace)
        self.server = ontology_server
        if not os.path.isfile(ontology_graph):
            self.graph = self._generate_new_ontology_graph()
        else:
            self.graph = Graph()
            self.graph.load(ontology_graph)
        atexit.register(self._save_ontology_graph)

    def search(self,pattern):
        return self.graph.triples(pattern)

    def get_server_uri(self,ontology_code=None,namespace=None,mask=None):
        if ontology_code is not None:
            return [s[0] for s in self.search((None,self.identifiers.ontology_code,Literal(ontology_code)))]
        elif namespace is not None:
            return [s[0] for s in self.search((None,self.identifiers.namespace,URIRef(namespace)))]
        elif mask is not None:
            return [s[0] for s in self.search((None,self.identifiers.mask,URIRef(mask)))]
        else:
            return [s[0] for s in self.search((None,self.identifiers.rdf_type,None))]
 
    def get_ontology_codes(self,server_uri=None,namespace=None,mask=None):
        if server_uri is not None:
            return [q[2] for q in self.search((URIRef(server_uri),self.identifiers.ontology_code,None))]
        elif namespace is not None:
            ontology_codes = []
            for uri in self.get_server_uri(namespace=namespace):
                ontology_codes = ontology_codes + self.get_ontology_codes(server_uri=uri)
            return ontology_codes
        elif mask is not None:
            ontology_codes = []
            for uri in self.get_server_uri(mask=mask):
                ontology_codes = ontology_codes + self.get_ontology_codes(server_uri=uri)
            return ontology_codes
        else:
            return [q[2] for q in self.search((None,self.identifiers.ontology_code,None))]
        
    def get_namespaces(self,server_uri=None,ontology_code=None,mask=None):
        if server_uri is not None:
            return [n[2] for n in self.search((URIRef(server_uri),self.identifiers.namespace,None))]
        elif ontology_code is not None:
            namespaces = []
            for uri in self.get_server_uri(ontology_code=ontology_code):
                namespaces = namespaces + self.get_namespaces(server_uri=uri)
            return namespaces
        elif mask is not None:
            namespaces = []
            for uri in self.get_server_uri(mask=mask):
                namespaces = namespaces + self.get_namespaces(server_uri=uri)
            return namespaces
        else:
            return [n[2] for n in self.search((None,self.identifiers.namespace,None))]

    def get_standard_mask(self,server_uri=None,ontology_code=None,namespace=None):
        if server_uri is not None:
            return [m[2] for m in self.search((URIRef(server_uri),self.identifiers.mask,None))]
        elif ontology_code is not None:
            masks = []
            for uri in self.get_server_uri(ontology_code=ontology_code):
                masks = masks + self.get_standard_mask(server_uri=uri)
            return masks
        elif namespace is not None:
            masks = []
            for uri in self.get_server_uri(namespace=namespace):
                masks = masks + self.get_standard_mask(server_uri=uri)
            return masks
        else:
            return [m[2] for m in self.search((None,self.identifiers.mask,None))]

    def add_ontology(self,ontology_code,namespace=None,mask=None):
        ontology_code = Literal(ontology_code)
        server_uri = self._build_server_uri(ontology_code)
        server_graphs = self.server._get_graph_names()

        if not server_uri in server_graphs:
            raise ValueError(f'{server_uri} is not found.')

        if namespace is None:
            namespace = self._build_namespace(ontology_code)
        namespace = URIRef(namespace)

        if mask is None:
            mask = self._build_standard_mask()
        mask = URIRef(mask)

        self.graph.add((server_uri,self.identifiers.rdf_type,self.identifiers.object_ontology))
        self.graph.add((server_uri,self.identifiers.ontology_code,ontology_code))
        self.graph.add((server_uri,self.identifiers.namespace,namespace))
        self.graph.add((server_uri,self.identifiers.mask,mask))

    def _build_ontology_code(self):
        pass
    
    def _build_server_uri(self,ontology_code):
        return URIRef(f'{self.identifiers.server_namespace}/{ontology_code}')

    def _build_namespace(self,ontology_code):
        ontology_qry = (None,self.identifiers.rdf_type,self.identifiers.owl_ontology)
        classes_qry = (None,self.identifiers.rdf_type,self.identifiers.owl_class)
        ontology_uri = self.server.select(ontology_qry,ontology_code=ontology_code,limit=None)
        ontology_uri = ontology_uri[0]["s"]["value"]

        classes = self.server.select(classes_qry,ontology_code=ontology_code,limit=10)
        common_prefix = ""
        for c in classes:
            c = c["s"]["value"]
            cpx = os.path.commonprefix([ontology_uri,c])
            if len(cpx) > len(common_prefix):
                common_prefix = cpx
        if common_prefix[-1] in "#\/":
            common_prefix = common_prefix[:-1]
        return common_prefix

    def _build_standard_mask(self):
        mask = URIRef("")
        return mask

    def _generate_new_ontology_graph(self):
        g = Graph()
        static_ontologies = StaticOntologyData()
        for ontology in static_ontologies:
            server_uri = ontology.server_uri
            ontology_code = ontology.ontology_code
            namespace = ontology.namespace
            standard_mask = ontology.standard_mask
            g.add((server_uri,self.identifiers.rdf_type,self.identifiers.object_ontology))
            g.add((server_uri,self.identifiers.ontology_code,Literal(ontology_code)))
            g.add((server_uri,self.identifiers.namespace,namespace))
            g.add((server_uri,self.identifiers.mask,standard_mask))
        return g

    def _save_ontology_graph(self):
        return self.graph.serialize(destination=ontology_graph, format="xml")