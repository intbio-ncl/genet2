import os
import re
from urllib.error import HTTPError

import rdflib
from Bio import Entrez
from Bio import GenBank

from app.enhancer.data_miner.database.interfaces.db_interface import DatabaseInterface

Entrez.email = "m.crowther1@ncl.ac.uk"
target_dbs = ['nuccore','protein']
predicate_blacklist = ["sequence","locus","date","contig","dblinks"]
object_blacklist = [[],"",None,{},()]
qualifier_object_whitelist = ["/product=","/type_material=","/mol_type=","/organism="]

class GenBankInterface(DatabaseInterface):
    def __init__(self,record_storage =  None):
        DatabaseInterface.__init__(self,"gbk")
        self.id_codes = [".-","nuccore","ncbi"]
        

    def get(self,identifier,timeout=10):
        if isinstance(identifier,rdflib.URIRef):
            dbs = [self._get_db_name(identifier)]
            identifier = self._get_name(identifier)
        else:
            dbs = target_dbs
        expected_fn = os.path.join(self.record_storage,str(identifier) + ".gbk")
        if not os.path.isfile(expected_fn):
            for db in dbs:
                if not self._is_valid_db_name(db):
                    raise ValueError(f'{db} is not a valid sub-db.')
                try:
                    net_handle = Entrez.efetch(db=db, id=identifier, rettype="gb", retmode="text")
                except HTTPError:
                    continue
                self._store_record(expected_fn,net_handle.read())
                net_handle.close()
                break
            else:
                raise ValueError(f"{identifier} Not Found.")
        record = self._generalise_get_results(expected_fn)
        return record


    def query(self,query,limit=5):
        query = f'"{query}"'
        for db in target_dbs:
            handle = Entrez.esearch(db=db, term=query,retmax=limit,idtype="acc")
            results = Entrez.read(handle)
            if results["Count"] != 0:
                return self._generalise_query_results(results)
        return []


    def count(self,query):
        count = 0
        query = f'"{query}"'
        handle = Entrez.egquery(term=query)
        record = Entrez.read(handle)
        handle.close()
        for row in record["eGQueryResult"]:
            if row["DbName"] in target_dbs:
                try:
                    count = count + int(row["Count"])
                except ValueError:
                    continue
        return count

    def is_record(self,uri):
        return False
    
    def sequence(self,sequence,similarity=None):
        return {}

    def get_uri(self,name):
        return []
        
    def get_metadata_identifiers(self):
        return [rdflib.URIRef("http://genbank2graph/features"),
                rdflib.URIRef("http://genbank2graph/taxonomy"),
                rdflib.URIRef("http://genbank2graph/references"),
                rdflib.URIRef("http://genbank2graph/definition")]

    def _generalise_get_results(self,filename):
        graph = rdflib.Graph()
        records = self._read_file(filename)
        for record in records:
            namespace = rdflib.Namespace("http://genbank2graph/")
            subject = namespace + rdflib.URIRef(record.locus)
            for attr, value in record.__dict__.items():
                if attr[0] == "_" or attr in predicate_blacklist or value in object_blacklist:
                    continue
                predicate = namespace + rdflib.URIRef(str(attr.replace(" ","")))
                if isinstance(value,(dict,list,set,tuple)): 
                    value = self._handle_entry(value,namespace,subject,predicate,graph)
                else:
                    literal = rdflib.Literal(value)
                    graph.add((subject,predicate,literal)) 
        return graph

    def _generalise_query_results(self,query_results):
        generalised_results = []
        if isinstance(query_results,list):
            for result in query_results:
                if "IdList" in result.keys():
                    for id in result["IdList"]:
                        generalised_results.append(id)

        elif isinstance(query_results,dict):
            if "IdList" in query_results.keys():
                for id in query_results["IdList"]:
                    generalised_results.append(str(id))
        return generalised_results

    def _handle_entry(self,entry,namespace,subject,predicate,graph):
        if isinstance(entry,dict):
            for k,v in entry.items():
                tmp_predicate = rdflib.URIRef(predicate + "/" + str(k.replace(" ","")))  
                graph = self._handle_entry(v,namespace,subject,tmp_predicate,graph)
        elif isinstance(entry,(list,set,tuple)):
            for e in entry:
                graph = self._handle_entry(e,namespace,subject,predicate,graph)
        elif isinstance(entry,GenBank.Record.Feature):
            for qualifier in entry.qualifiers:
                if qualifier.key in qualifier_object_whitelist:
                    graph = self._handle_entry(qualifier.value,namespace,subject,predicate,graph)
        elif isinstance(entry,GenBank.Record.Reference):
            graph = self._handle_entry(entry.title,namespace,subject,predicate,graph)

        else:
            obj = rdflib.Literal(entry.replace(" ","_"))
            graph.add((subject,predicate,obj))
        return graph

    def _get_name(self,subject):
        split_subject = self._split(subject)
        return split_subject[-1]

    def _get_db_name(self,uri):
        uri_split = self._split(uri)
        for part in uri_split:
            if self._is_valid_db_name(part):
                return part
        return None
    
    def _split(self,uri):
        return re.split('#|\/|:', uri)

    def _is_valid_db_name(self,db_name):
        handle = Entrez.einfo()
        databases = Entrez.read(handle)
        handle.close()
        if db_name in databases["DbList"]:
            return True
        else:
            return False

    def _read_file(self,fn):
        records = []
        with open(fn) as handle:
            for record in GenBank.parse(handle):
                records.append(record)
        return records









