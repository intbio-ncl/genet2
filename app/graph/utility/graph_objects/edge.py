import re
import validators

class Edge:
    def __init__(self,n,v,type,id=None,**kwargs):
        self.type = str(type)
        self.id=id
        if isinstance(type,list):
            self.properties = {}
        else:
            self.properties = {"name" : _get_name(type)} if "name" not in kwargs else {}
        self._update(kwargs)
        self.n = n
        self.v = v

    def duplicate(self):
        return self.__class__(self.n.duplicate(),self.v.duplicate(),
                              self.type,**self.properties)
                              
    def __str__(self):
        return f'{self.n} - {self.type} - {self.v}'

    def __eq__(self, obj):
        if not isinstance(obj, Edge):
            return False
        if obj.n == self.n and obj.type == self.type and obj.v == self.v:
            return True
        return False

    def __hash__(self):
        return hash(str(self.type+self.n.key+self.v.key))
        
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
            if validators.url(k):
                setattr(self,_get_name(k),v)
            elif isinstance(v,(set,list,tuple)) and hasattr(self,_get_name(k)):
                setattr(self, k, self[k]+v)
            else:
                setattr(self, k, v)

            if k != "id":
                if k not in self.properties:
                    continue
                if isinstance(v,(set,list,tuple)):
                    self.properties[k] = [n for n in self.properties[k] if n not in v]
                else:
                    del self.properties[k]
                    self.properties[k] = v

    def _update(self,items):
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

    def _replace(self,items):
        for k,v in self.properties.items():
            if validators.url(k):
                delattr(self,_get_name(k))
            else:
                delattr(self,k)
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

    def get_type(self):
        return self.type

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