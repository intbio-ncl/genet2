import os
import sys

import rdflib
from Bio import ExPASy
from Bio import SwissProt

from app.enhancer.data_miner.database.interfaces.db_interface import DatabaseInterface

class SwissProtInterface(DatabaseInterface):
    def __init__(self,record_storage =  None):
        if record_storage is None:
            record_storage = "records"
        self.record_storage = os.path.join(record_storage,"swissprot")
        
    def get(self,id):
        """Open and Read a Swiss-Prot file locally from remote source (ExPASy database)
            Swiss-Prot file over the internet from the ExPASy database.
            Input must be a accession number stored on the swissprot site.
        """
        handle = ExPASy.get_sprot_raw(id)
        record = SwissProt.read(handle)
        return record

    def query(self,query_string):
        sys.stderr.write("Query for Swissprot is not Implemented.")
        return []

    def count(self,query_string):
        sys.stderr.write("Count for Swissprot is not Implemented.")
        return []

    def related(self,id):
        sys.stderr.write("Related for Swissprot is not Implemented.")
        return []

    def generalise_get_results(self,get_results):
        general_graph = rdflib.Graph()
        prune_attr = ["references","created","sequence_update","annotation_update","features","sequence"]
        prune_value = [[],"",None,{},()]

        if not isinstance(get_results,(list,tuple,set)):
            get_results = [get_results]

        namespace = rdflib.Namespace("http://swissprot2graph/")

        for result in get_results:
            subject = namespace + rdflib.URIRef(result.entry_name)
            for attr, value in result.__dict__.items():

                if attr[0] == "_" or attr in prune_attr or value in prune_value:
                    continue
                
                predicate = namespace + rdflib.URIRef(str(attr.replace(" ","")))

                if isinstance(value,(dict,list,set,tuple)): 
                    value = _handle_entry(value,namespace,subject,predicate,general_graph)
                else:
                    object = rdflib.Literal(value)
                    general_graph.add((subject,predicate,object)) 
    
        return general_graph

    def generalise_query_results(self,query_results):
        generalised_results = []        
        return generalised_results
    

def _handle_entry(entry,namespace,subject,predicate,graph):
    if isinstance(entry,dict):
        for k,v in entry.items():
            tmp_predicate = rdflib.URIRef(predicate + "/" + str(k.replace(" ","")))  
            graph = _handle_entry(v,namespace,subject,tmp_predicate,graph)
    elif isinstance(entry,(list,set,tuple)):
        for index, e in enumerate(entry):
            tmp_predicate = rdflib.URIRef(predicate + "/" + str(index))  
            graph = _handle_entry(e,namespace,subject,tmp_predicate,graph)
    else:
        object = rdflib.Literal(str(entry).replace(" ","_"))
        graph.add((subject,predicate,object))
    return graph





