import os
import re

from urllib.error import URLError
import rdflib
from SPARQLWrapper import SPARQLWrapper,JSON
import operator

from app.enhancer.data_miner.ontology.server_interface.utility.query_builder import QueryBuilder
from app.enhancer.data_miner.ontology.server_interface.utility.ontology_graph import OntologyGraph


base_server_uri = "http://localhost:8890/sparql"
default_namespace = "http://ontology_server/"

class OntologyInterface:
    def __init__(self):
        self.sparql = SPARQLWrapper(base_server_uri)
        self.query_builder = QueryBuilder()
        self.namespace = self._get_namespace()
        self.ontology_graph = OntologyGraph(self,self.namespace)
        
        
    def select(self,query,ontology_code = None,limit=None):
        results = []
        server_uris = self.get_server_uri(ontology_code)
        for server_uri in server_uris:
            query = self.query_builder.select(query,server_uri)
            result = self._run_query(str(query))
            if result is not None:
                results = results + self._normalise_results(result,query.triples)
        return results
        
    def get_ontology_codes(self,subject=None,server_uri=None,namespace=None,mask=None):
        if server_uri is not None:
            return self.ontology_graph.get_ontology_codes(server_uri=server_uri)
        elif namespace is not None:
            return self.ontology_graph.get_ontology_codes(namespace=namespace)
        elif mask is not None:
            return self.ontology_graph.get_ontology_codes(mask=mask)
        elif subject is not None:
            prefix = rdflib.URIRef(self._get_prefix(subject))
            ontology_codes = self.ontology_graph.get_ontology_codes(namespace=prefix)
            if len(ontology_codes) != 0:
                return ontology_codes

            p_ontology_codes = [item for uri in self._split(subject)[-2:] 
                                for item in re.split("_|\\.",uri)]
            ontology_codes = [str(q) for q in self.ontology_graph.get_ontology_codes()]
            for ontology_code in p_ontology_codes:
                if ontology_code in ontology_codes:
                    return [rdflib.Literal(ontology_code)]
                if ontology_code.upper() in ontology_codes:
                    return [rdflib.Literal(ontology_code.upper())]
            raise ValueError(f'{subject} does not correlate to an ontology in this server.')
        else:
            return self.ontology_graph.get_ontology_codes()

    def get_namespaces(self,server_uri=None,ontology_code=None,mask=None):
        namespaces = self.ontology_graph.get_namespaces(server_uri=server_uri,
                                                        ontology_code=ontology_code,
                                                        mask=mask)
        return namespaces

    def get_server_uri(self,ontology_code=None,namespace=None,mask=None):
        server_uris = self.ontology_graph.get_server_uri(ontology_code=ontology_code,
                                                         namespace=namespace,
                                                         mask=mask)
        return server_uris

    def get_standard_mask(self,server_uri=None,ontology_code=None,namespace=None):
        masks = self.ontology_graph.get_standard_mask(server_uri=server_uri,
                                                      ontology_code=ontology_code,
                                                      namespace=namespace)
        return masks


    def get_new_ontologies(self):
        server_graphs = self._get_graph_names()
        local_graphs = self.ontology_graph.get_server_uri()
        new_ontologies = []
        for s_graph in server_graphs:
            s_prefix = self._get_prefix(s_graph)
            if s_prefix != self.namespace:
                continue
            if s_graph in local_graphs:
                continue    
            new_ontologies.append(s_graph)
            new_qry_code = self._split(s_graph)[-1]
            self.ontology_graph.add_ontology(new_qry_code)
        return new_ontologies


    def _run_query(self,query_string):
        try:
            self.sparql.setQuery(query_string)
            self.sparql.setReturnFormat(JSON)
            ret = self.sparql.query()
            ret = ret.convert()
            return ret
        except URLError:
            return None

    def _normalise_results(self,results,triple_store):
        def _swap_result(triple,result):
            swapped_triple = []
            for element in triple:
                if element is None or element[0] != "?":
                    swapped_triple.append(element)
                    continue
                param = element[1:]
                try:
                    element_result = result[param]
                except KeyError:
                    return None
                e_type = element_result["type"]
                e_val = element_result["value"]
                if e_type == "uri":
                    element = rdflib.URIRef(e_val)
                else:
                    element = rdflib.Literal(e_val)
                swapped_triple.append(element)
            return tuple(swapped_triple)

        n_results = []
        results = results["results"]["bindings"]
        for result in results:
            for triple in triple_store:
                s_result = _swap_result(triple,result)
                if s_result is not None:
                    n_results.append(s_result)
        return list(set(n_results))
            

    def _get_graph_names(self):
        qry_string = self.query_builder.get_graphs()
        response = self._run_query(str(qry_string))
        if response is None or "results" not in response:
            return default_namespace
        graphs = []
        for r in response["results"]["bindings"]:
            graphs.append(rdflib.URIRef(r["g"]["value"]))
        return graphs

    def _get_namespace(self):
        graphs = self._get_graph_names()
        prefixes = {}
        for r in graphs:
            prefix = self._get_prefix(r)
            if prefix in prefixes.keys():
                prefixes[prefix] = prefixes[prefix] + 1
            else:
                prefixes[prefix] = 1
        prefix = max(prefixes.items(), key=operator.itemgetter(1))[0]
        return prefix

    def _get_name(self,subject):
        split_subject = self._split(subject)
        if len(split_subject[-1]) == 1 and split_subject[-1].isdigit():
            return split_subject[-2]
        else:
            return split_subject[-1]
            
    def _get_prefix(self,uri):
        parts = self._split(uri)
        split_len = 4
        remove_parts = parts[split_len:]
        remove_val = 0
        for p_p in remove_parts:
            remove_val = remove_val + len(p_p) + 1
        prefix = uri[:-remove_val]
        return prefix   

    def _split(self,uri):
        return re.split('#|\/|:', str(uri))



