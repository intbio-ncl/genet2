import validators
import re

class GraphObject:
    def __init__(self,graph,labels,**kwargs):
        if not isinstance(labels,(list,set,tuple)):
            labels = [labels]
            
        self.labels = labels
        self.properties = {}
        self._update(kwargs)
        self._graph = graph

    def __hash__(self):
        return hash(str(self.labels))

    def __str__(self):
        return "|".join(["`"+ str(l) +"`" for l in self.labels])

    def __getitem__(self, item):
        return self.properties[item]

    def update(self,go):
        if not isinstance(go,self.__class__):
            raise ValueError(f'{go} is not valid class to update with {self}')
        self._update(go.get_properties())

    def _update(self,items):
        for k,v in items.items():
            if validators.url(k):
                setattr(self,_get_name(k),v)
            else:
                setattr(self, k, v)
            if k != "id":
                self.properties[k] = v

    def get_labels(self):
        return self.labels

    def get_properties(self):
        return self.properties

    def add_property(self,key,value):
        self.properties[key] = value

def _get_name(subject):
    split_subject = _split(subject)
    if len(split_subject[-1]) == 1 and split_subject[-1].isdigit():
        return split_subject[-2]
    else:
        return split_subject[-1]


def _split(uri):
    return re.split('#|\/|:', uri)