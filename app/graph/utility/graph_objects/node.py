import re
import validators
from urllib.parse import urlparse
class Node:
    def __init__(self,key,type=None,id=None, **kwargs):
        self.key = str(key)
        self.type = str(type)
        self.id=id
        self.properties = {}
        if "name" not in kwargs:
            kwargs["name"] = _get_name(key)
        self._update(kwargs)

    def duplicate(self):
        return self.__class__(self.key,self.type,**self.properties)
        
    def __eq__(self, obj):
        if not isinstance(obj, Node):
            return False
        if obj.key == self.key:
            return True
        return False
        
    def __hash__(self):
        return hash(str(self.key))

    def __str__(self):
        return self.key

    def __getitem__(self, item):
        return self.properties[item]

    def update(self,go):
        if isinstance(go,self.__class__):
            self._update(go.get_properties())
            return
        elif isinstance(go,dict):
            self._update(go)
            return
        raise ValueError(f'{go} is not valid class to update with {self}')

    def remove(self,go):
        if isinstance(go,self.__class__):
            self._update(go.get_properties())
            return
        elif isinstance(go,dict):
            self._update(go)
            return
        raise ValueError(f'{go} is not valid class to remove with {self}')

    def replace(self,go):
        if isinstance(go,self.__class__):
            self._replace(go.get_properties())
            return
        elif isinstance(go,dict):
            self._replace(go)
            return
        raise ValueError(f'{go} is not valid class to remove with {self}')

    def remove(self,items):
        for k,v in items.items():
            try:
                self[k]
            except KeyError:
                continue
            if validators.url(k):
                setattr(self,_get_name(k),v)
            elif isinstance(v,(set,list,tuple)) and hasattr(self,_get_name(k)):
                if isinstance(self[k],list):
                    setattr(self, k, self[k]+v)
                else:
                    setattr(self,k,[self[k]] + v)
            else:
                setattr(self, k, v)

            if k != "id":
                if k not in self.properties:
                    continue
                if isinstance(v,(set,list,tuple)):
                    self.properties[k] = [n for n in self.properties[k] if n not in v]
                    if self.properties[k] == []:
                        del self.properties[k]
                else:
                    del self.properties[k]
                    self.properties[k] = v

    def _update(self,items):
        for k,v in items.items():
            up = urlparse(k)
            if up.netloc != "":
                setattr(self,_get_name(k),v)
            elif isinstance(v,(set,list,tuple)) and hasattr(self,_get_name(k)):
                if isinstance(self[k],list):
                    setattr(self, k, list(set(self[k]+v)))
                else:
                    setattr(self,k,list(set([self[k]] + v)))
            else:
                setattr(self, k, v)
            if k != "id":
                if k not in self.properties:
                    self.properties[k] = v
                if isinstance(v,(set,list,tuple)):
                    self.properties[k] = list(set(self.properties[k]+v))
                else:
                    self.properties[k] = v

    def _replace(self,items):
        for k,v in self.properties.items():
            try:
                delattr(self,k)
            except AttributeError:
                continue
        self.properties.clear()
        for k,v in items.items():
            if validators.url(k):
                setattr(self,_get_name(k),v)
            elif isinstance(v,(set,list,tuple)) and hasattr(self,_get_name(k)):
                setattr(self, k, self[k]+v)
            else:
                setattr(self, k, v)
            if k != "id":
                if k not in self.properties:
                    self.properties[k] = v
                if isinstance(v,(set,list,tuple)):
                    self.properties[k] = list(set(self.properties[k]+v))
                else:
                    self.properties[k] = v

    def get_key(self):
        return self.key

    def get_type(self):
        return self.type

    def get_labels(self):
        if self.type is None or self.type == "None":
            return [self.key]
        return [self.key,self.type]

    def get_properties(self):
        return self.properties

    def add_property(self,key,value):
        self.properties[key] = value

    def remove_property(self,k):
        del self.properties[k]
        
def _get_name(subject):
    split_subject = _split(subject)
    if len(split_subject[-1]) == 1 and split_subject[-1].isdigit():
        return split_subject[-2]
    else:
        return split_subject[-1]


def _split(uri):
    return re.split('#|\/|:', uri)
