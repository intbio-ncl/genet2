from app.enhancer.data_miner.database.utility import DatabaseUtility

blacklist_inputs = [None,""]
class DatabaseHandler:
    def __init__(self):
        self._db_util = DatabaseUtility()
        for k,v in self._db_util.db_mapping_calls.items():
            setattr(DatabaseHandler, k, k)
        
    def get(self,identity):
        if identity in blacklist_inputs:
            return None
        if str.isdigit(identity):
            return None
        for db in self._get_potential_db_names(identity):
            record = self._db_util.get(identity,db_name=db)
            if record is not None:
                return record
        return None

    def count(self,query):
        for db in self._db_util.db_mapping_calls.keys():
            yield self._db_util.count(query,db)

    def query(self,query,lazy=False):
        if lazy:
            for db in self._db_util.db_mapping_calls.keys():
                res = self._db_util.query(query,db)
                if len(res) > 0:
                    yield res
                    return
        else:
            for db in self._db_util.db_mapping_calls.keys():
                yield self._db_util.query(query,db)

    def is_record(self,identity):
        for db in self._db_util.db_mapping_calls.keys():
            if self._db_util.is_record(identity,db):
                return True
        return False

    def sequence_search(self,seqeunce,similarity=None):
        for db in self._db_util.db_mapping_calls.keys():
            s = self._db_util.sequence(seqeunce,db,similarity=similarity)
            if s is not None and len(s) > 0:
                return s
        return None

    def get_uri(self,name):
        for db in self._db_util.db_mapping_calls.keys():
            s = self._db_util.get_uri(name,db)
            if s != []:
                return s[0]
        return None
        
    def find_uses(self):
        pass

    def get_metadata_identifiers(self):
        return self._db_util.get_metadata_identifiers()

    def _get_potential_db_names(self,identity):
        potential_codes = self._db_util.get_potential_db_names(identity)
        if len(potential_codes) == 0:
            return list(self._db_util.db_mapping_calls.keys())
        return potential_codes
