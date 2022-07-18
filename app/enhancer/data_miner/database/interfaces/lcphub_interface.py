from graph.knowledge.data_miner.database.interfaces.abstract_hub_interface import AbstractSynBioHubInterface

lcp_url_base = "https://synbiohub.programmingbiology.org/"

class LCPHubInterface(AbstractSynBioHubInterface):
    def __init__(self):
        AbstractSynBioHubInterface.__init__(self, "lcp")
        self.id_codes = ["programmingbiology"]
        

    def get(self,identifier,prune=True):
        result = super().get(identifier,lcp_url_base,prune)
        return result

    def query(self,query,search_limit=5):
        result = super().query(query,lcp_url_base,limit=search_limit)
        return result

    def count(self,query):
        result = super().count(query,lcp_url_base)
        return result