import os
import re
from abc import ABCMeta, abstractmethod

import rdflib
import requests
from requests.exceptions import ConnectionError, ReadTimeout
import json

from graph.knowledge.data_miner.database.interfaces.db_interface import DatabaseInterface
from utility.sbol_identifiers import identifiers


metadata_predicates = [identifiers.predicates.display_id,
                       identifiers.predicates.title,
                       identifiers.predicates.description,
                       identifiers.predicates.mutable_description,
                       identifiers.predicates.mutable_notes,
                       identifiers.predicates.mutable_provenance]

predicate_whitelist = metadata_predicates + [identifiers.predicates.role,
                                             identifiers.predicates.type]


class AbstractSynBioHubInterface(DatabaseInterface):
    def __init__(self,record_storage =  None):
        if record_storage is not None:
            record_storage = os.path.join("hubs",record_storage)
        DatabaseInterface.__init__(self, record_storage)
        self._query_builder = QueryBuilder()

    @abstractmethod
    def get(self,identifier,base,prune=True):
        collections = self._get_collection(identifier,base)
        identifier = self._get_name(identifier)
        expected_fn = os.path.join(self.record_storage,identifier + ".xml")
        if not os.path.isfile(expected_fn):
            for collection in collections:
                get_uri = f'{base}public/{collection}/{identifier}/sbol'
                try:

                    r = requests.get(get_uri,timeout=10)
                except (ConnectionError,ReadTimeout):
                    print(f"WARN:: GET request for {base} timed out.")
                    continue
                try:
                    r.raise_for_status()
                except requests.exceptions.HTTPError:
                    continue
                self._store_record(expected_fn,r.text)
                break
            else:
                raise ValueError(f'Unable to find record given {identifier}')

        graph = self._load_graph(expected_fn)
        if prune:
            graph = self._generalise_get_results(graph)
        return graph

    @abstractmethod
    def query(self,query,base,limit=5):
        sparql_query = self._query_builder.query(query,limit)
        results = self._sparql(sparql_query,base)
        return self._generalise_query_results(results)

    @abstractmethod
    def count(self,query,base):
        sparql_query = self._query_builder.count(query)
        count = self._sparql(sparql_query,base)
        return self._generalise_count_results(count)

    def get_metadata_identifiers(self):
        return metadata_predicates

    def get_root_collections(self,base):
        response = requests.get(
        f'{base}rootCollections',
        params={'X-authorization': 'token'},
        headers={'Accept': 'text/plain'},)
        roots = json.loads(response.text)
        roots = [k['uri'].split("/")[4] for k in roots]
        return roots

    def _sparql(self,query,base):
        query = requests.utils.quote(query)
        synbiohub_url = f'{base}sparql?query={query}'
        r = requests.get(synbiohub_url,headers={'Accept': 'application/json'})
        r.raise_for_status()    
        return json.loads(r.content)

    def _generalise_query_results(self,query_results):
        g_query_results = []
        if "results" not in query_results.keys():
            return g_query_results
        if "bindings" not in query_results["results"].keys():
            return g_query_results
        for result in query_results["results"]["bindings"]:
            if "subject" not in result.keys():
                continue
            if "value" not in result["subject"].keys():
                continue
            uri = rdflib.URIRef(result["subject"]["value"])
            g_query_results.append(uri)
        return g_query_results 

    def _generalise_count_results(self,count_result):
        if "results" not in count_result.keys():
            return 0
        if "bindings" not in count_result["results"].keys():
            return 0
        for result in count_result["results"]["bindings"]:
            if "count" not in result.keys():
                continue
            if "value" not in result["count"].keys():
                continue
            try:
                return int(result["count"]["value"])
            except ValueError:
                return 0
        return 0 

    def _generalise_get_results(self,graph):
        for s,p,o in graph:
            if p not in predicate_whitelist:
                graph.remove((None,p,None))    
        return graph

    def _get_name(self,subject):
        split_subject = self._split(subject)
        if len(split_subject[-1]) == 1 and split_subject[-1].isdigit():
            return split_subject[-2]
        else:
            return split_subject[-1]

    def _get_collection(self,identifier,base):
        if not isinstance(identifier,rdflib.URIRef):
            return self.get_root_collections(base)
        uri_split = self._split(identifier)
        if len(uri_split[-1]) == 1 and uri_split[-1].isdigit():
            return [uri_split[-3]]
        else:
            return [uri_split[-2]]
    
    def _split(self,uri):
        return re.split('#|\/|:', uri)






class QueryBuilder:
    def __init__(self):
        self.metadata_predicates = {"title" : "dcterms",
                                    "description" : "dcterms",
                                    "mutableNotes" : "sbh",
                                    "mutableDescription" : "sbh",
                                    "mutableProvenance" : "sbh"}

        self.prefixes = ("PREFIX sbol2: <http://sbols.org/v2#>\n" + 
                        "PREFIX dcterms: <http://purl.org/dc/terms/>\n" +
                        "PREFIX sbh: <http://wiki.synbiohub.org/wiki/Terms/synbiohub#>\n"+
                        "PREFIX igem: <http://wiki.synbiohub.org/wiki/Terms/igem#>\n"+
                        "PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>\n"+
                        "PREFIX dc: <http://purl.org/dc/elements/1.1/>\n"+
                        "PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>\n"+
                        "PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>\n")

    
    def query(self,qry_string,limit=5):
        spql_string = f'{self.prefixes}\nSELECT DISTINCT ?subject\n'        
        spql_string = f'{spql_string}{self._where_meta_search(qry_string)}'
        spql_string = f'{spql_string} LIMIT {str(limit)}'
        return spql_string


    def count(self,qry_string):
        spql_string = f'{self.prefixes}\nSELECT (sum(?tempcount) as ?count) \nWHERE {{{{'
        spql_string = f'{spql_string}\n   SELECT (count(distinct ?subject) as ?tempcount)\n'
        spql_string = f'{spql_string}{self._where_meta_search(qry_string,1)}'
        spql_string = f'{spql_string}\n}}}}'
        return spql_string

    def _where_meta_search(self,qry_string,indent_level=0):
        indent = "   " * indent_level
        next_indent_level = indent_level+1
        parts = qry_string.split(" ")
        if len(parts) == 0:
            raise ValueError(f"Invalid Input QRY: {qry_string}")
        
        where_string = f'{indent}WHERE {self._contains_filter(parts,next_indent_level)}'
        where_string = f'{where_string}{self._top_level(next_indent_level)}'
        where_string = f'{where_string}{self._meta_optional(next_indent_level)}'
        where_string = f'{where_string}{indent}}}'
        return where_string


    def _contains_filter(self,parts,indent_level = 2):
        indent = "   " * indent_level
        next_indent_level = indent_level + 1
        filter_string = f'{{\n{indent}FILTER ('
        for index,p in enumerate(parts):
            contain_grp = self._contains_group(p,next_indent_level)
            if index < len(parts) - 1:
                filter_string = f'{filter_string}({contain_grp})\n{indent}&&'
            else:
                filter_string = f'{filter_string}({contain_grp})'
        filter_string = f'{filter_string})'
        return filter_string

    def _contains_group(self,item,indent_level=2):
        indent = "   " * indent_level
        contain_grp = ""
        for p_index,predicate in enumerate(self.metadata_predicates.keys()):
            contain_grp = f"{contain_grp}\n{indent}CONTAINS(lcase(?{predicate}), lcase('{item}'))"
            if p_index < len(self.metadata_predicates) - 1:
                contain_grp = f'{contain_grp} ||'
        return contain_grp

    def _top_level(self,indent_level=1):
        indent = "   " * indent_level
        return f'\n{indent}?subject sbh:topLevel ?subject .\n'

    def _meta_optional(self,indent_level=1):
        meta_str = ""
        indent = "   " * indent_level
        for predicate,ns in self.metadata_predicates.items():
            meta_str = f'{meta_str}{indent}OPTIONAL {{ ?subject {ns}:{predicate} ?{predicate} .}}\n'
        return meta_str