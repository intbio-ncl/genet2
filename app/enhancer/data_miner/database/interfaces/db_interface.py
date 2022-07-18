import os
import json
from abc import ABCMeta, abstractmethod

import rdflib
import requests


base_storage = os.path.join(os.path.dirname(__file__),"records")

class DatabaseInterface:
    __metaclass__ = ABCMeta
    def __init__(self,record_storage):
        self.record_storage = os.path.join(base_storage,record_storage)
        self.id_codes = []
        
    @abstractmethod
    def get(self,id):
        pass

    @abstractmethod
    def query(self,query_string):
        pass

    @abstractmethod
    def count(self,query_string):
        pass

    @abstractmethod
    def is_record(self,identity):
        pass
    
    def _load_graph(self,fn):
        record_graph = rdflib.Graph()
        record_graph.load(fn)
        return record_graph
        
    def _store_record(self,target,record):
        try:
            os.makedirs(self.record_storage)
        except FileExistsError:
            pass
        
        if os.path.isfile(target):
            return target
        f = open(target,"a")
        f.write(record)
        f.close()
        return target



