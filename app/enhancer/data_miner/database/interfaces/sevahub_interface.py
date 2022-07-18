from graph.knowledge.data_miner.database.interfaces.abstract_hub_interface import AbstractSynBioHubInterface

sevahub_url_base = "http://sevahub.es/"


class SevaHubInterface(AbstractSynBioHubInterface):
    def __init__(self,record_storage =  None):
        AbstractSynBioHubInterface.__init__(self, "svh")
        self.id_codes = ["sevahub","Canonical"]
        

    def get(self,identifier,prune=True):
        result = super().get(identifier,sevahub_url_base,prune)
        return result

    def query(self,query,search_limit=5):
        result = super().query(query,sevahub_url_base,limit=search_limit)
        return result

    def count(self,query):
        result = super().count(query,sevahub_url_base)
        return result