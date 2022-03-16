from app.utility.sbol_connector.interfaces.abstract_hub_interface import AbstractSynBioHubInterface



class SynBioHubInterface(AbstractSynBioHubInterface):
    def __init__(self):
        AbstractSynBioHubInterface.__init__(self, "sbh")
        self.base = "https://synbiohub.org/"

    def get(self,identifier,output=None):
        result = super().get(identifier,self.base,output)
        return result

    def query(self,query,search_limit=5):
        result = super().query(query,self.base,limit=search_limit)
        return result

    def count(self,query):
        result = super().count(query,self.base)
        return result

    def submit(self,filename):
        result = super().submit(filename,self.base)
        return result



