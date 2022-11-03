import os
import shutil
import atexit
import time
from urllib.error import HTTPError

from app.enhancer.data_miner.database.interfaces import hub_interface
from app.enhancer.data_miner.database.interfaces.genbank_interface import GenBankInterface

class DatabaseUtility:
    def __init__(self):
        self.db_mapping_calls = {"synbiohub" : hub_interface.SynBioHubInterface(),
                                 "lcp"       : hub_interface.LCPHubInterface(),
                                 "sevahub"   : hub_interface.SevaHubInterface(),
                                 "genbank"   : GenBankInterface()}
        atexit.register(self._remove_records)

    def get(self,id,db_name):
        try:
            record = self.db_mapping_calls[db_name].get(id)
            return record
        except (HTTPError,ValueError,KeyError):
            return None
    
    def count(self,query,db_name):
        return self.db_mapping_calls[db_name].count(query)

    def query(self,query,db_name,limit = 5):
        returned = False
        attempts = 0
        while not returned and attempts < 5:
            try:
                return self.db_mapping_calls[db_name].query(query,limit=limit)
            except HTTPError:
                print(f'WARN:: Err querying with {query} for db: {db_name}. Attempt: {attempts}')
                attempts = attempts + 1
                time.sleep(5)
        return []

    def is_record(self,identity,db_name):
        db = self.db_mapping_calls[db_name]
        if not hasattr(db,"base") or db.base not in identity:
            return False
        return db.is_triple(s=identity)

    def get_uri(self,name,db_name):
        return self.db_mapping_calls[db_name].get_uri(name)

    def sequence(self,sequence,db_name,similarity=None):
        return self.db_mapping_calls[db_name].sequence(sequence,similarity=similarity)

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

        




