import os
import re
from abc import abstractmethod

import rdflib
import requests
import json

from app.utility.sbol_connector.interfaces.query_builder import QueryBuilder
curr_dir = os.path.dirname(os.path.realpath(__file__))
class AbstractSynBioHubInterface:
    def __init__(self,record_storage):
        self.record_storage = os.path.join(curr_dir,"hubs",record_storage)
        self._query_builder = QueryBuilder()

    @abstractmethod
    def get(self,identifier,base,output=None):
        collections = self._get_collection(identifier,base)
        identifier = self._get_name(identifier)
        if output is None:
            output = os.path.join(self.record_storage,identifier + ".xml")
        if not os.path.isfile(output):
            for collection in collections:
                get_uri = f'{base}public/{collection}/{identifier}/sbol'
                r = requests.get(get_uri)
                try:
                    r.raise_for_status()
                except requests.exceptions.HTTPError:
                    continue
                self._store_record(output,r.text)
                break
            else:
                raise ValueError(f'Unable to find record given {identifier}')
        graph = self._load_graph(output)
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
    
    @abstractmethod
    def submit(self,filename,base):
        raise NotImplementedError("Submit Synbiohub is not implemented.")

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

    def _load_graph(self,fn):
        record_graph = rdflib.Graph()
        record_graph.parse(fn)
        return record_graph
        
    def _store_record(self,target,record):
        try:
            os.makedirs(self.record_storage)
        except FileExistsError:
            pass
        
        if os.path.isfile(target):
            return target
        f = open(target,"a")
        f.write(record)
        f.close()
        return target

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