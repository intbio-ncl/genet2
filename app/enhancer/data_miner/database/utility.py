import os
import shutil
import atexit
import time

from rdflib import Graph
from urllib.error import HTTPError

from graph.knowledge.data_miner.database.interfaces.synbiohub_interface import SynBioHubInterface
from graph.knowledge.data_miner.database.interfaces.sevahub_interface import SevaHubInterface
from graph.knowledge.data_miner.database.interfaces.lcphub_interface import LCPHubInterface
from graph.knowledge.data_miner.database.interfaces.genbank_interface import GenBankInterface

class DatabaseUtility:
    def __init__(self):
        self.db_mapping_calls = {"synbiohub" : SynBioHubInterface(),
                                 "genbank"   : GenBankInterface(),
                                 "sevahub"   : SevaHubInterface(),
                                 "lcp"       : LCPHubInterface()}
        atexit.register(self._remove_records)

    def get(self,id,db_name):
        try:
            record = self.db_mapping_calls[db_name].get(id)
            return record
        except (HTTPError,ValueError,KeyError):
            return None

    def count(self,query,db_name):
        return self.db_mapping_calls[db_name].count(query)

    def query(self,query,db_name,search_limit = 5):
        returned = False
        attempts = 0
        while not returned and attempts < 5:
            try:
                return self.db_mapping_calls[db_name].query(query,search_limit=search_limit)
            except HTTPError:
                print(f'WARN:: Err querying with {query} for db: {db_name}. Attempt: {attempts}')
                attempts = attempts + 1
                time.sleep(5)
        return []

    def is_record(self,identity):
        for db in self.db_mapping_calls.values():
            if any(code.lower() in identity.lower() for code in db.id_codes):
                return True
        return False

    def get_metadata_identifiers(self):
        return [identity for db in self.db_mapping_calls.values() 
                         for identity in db.get_metadata_identifiers()]
         
    def get_potential_db_names(self,identity):
        potential_dbs = []
        for name,db in self.db_mapping_calls.items():
            if any(code.lower() in identity.lower() for code in db.id_codes):
                potential_dbs.append(name)
        return potential_dbs

    def _remove_records(self):
        print("WARN:: Stopped deleting records on db util for testing.")
        return None
        if os.path.isdir(record_storage):
            shutil.rmtree(record_storage) 

        




