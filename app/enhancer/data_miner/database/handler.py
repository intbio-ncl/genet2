from graph.knowledge.data_miner.database.utility import DatabaseUtility

class DatabaseHandler:
    def __init__(self,offline=False):
        self.is_offline = offline
        if not offline:
            self._db_util = DatabaseUtility()

        for k,v in self._db_util.db_mapping_calls.items():
            setattr(DatabaseHandler, k, k)
        
    def get(self,identity):
        if self.is_offline : return None
        for db in self._get_potential_db_names(identity):
            record = self._db_util.get(identity,db_name=db)
            if record is not None:
                return record
        return None

    def count(self,query):
        if self.is_offline: return []
        for db in self._db_util.db_mapping_calls.keys():
            yield self._db_util.count(query,db)

    def query(self,query):
        if self.is_offline: return []
        for db in self._db_util.db_mapping_calls.keys():
            yield self._db_util.query(query,db)

    def is_record(self,identity):
        if self.is_offline: return False
        return self._db_util.is_record(identity)

    def get_metadata_identifiers(self):
        if self.is_offline: return []
        return self._db_util.get_metadata_identifiers()

    def _get_potential_db_names(self,identity):
        if self.is_offline : return []
        potential_codes = self._db_util.get_potential_db_names(identity)
        if len(potential_codes) == 0:
            return list(self._db_util.db_mapping_calls.keys())
        return potential_codes
