from graph.knowledge.data_miner.database.interfaces.abstract_hub_interface import AbstractSynBioHubInterface

synbiohub_url_base = "https://synbiohub.org/"

class SynBioHubInterface(AbstractSynBioHubInterface):
    def __init__(self):
        AbstractSynBioHubInterface.__init__(self, "sbh")
        self.id_codes = ["bba_","sbh","synbiohub"]
        

    def get(self,identifier,prune=True):
        result = super().get(identifier,synbiohub_url_base,prune)
        return result

    def query(self,query,search_limit=5):
        result = super().query(query,synbiohub_url_base,limit=search_limit)
        return result

    def count(self,query):
        result = super().count(query,synbiohub_url_base)
        return result
