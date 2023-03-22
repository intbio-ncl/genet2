from rdflib import URIRef,Literal
from identifiers import identifiers
from datatype.datatype import Input,Output,Integer,String

class Property:
    def __init__(self,range=None,properties=[],equivalents = [],default_value=None):
        name = self.__class__.__name__.lower()[0] + self.__class__.__name__[1:]
        self.property = URIRef(identifiers.namespaces.nv + name)
        if not isinstance(range, list):
            range = [range]
        self.range = range
        self.properties = properties
        self.equivalents = equivalents
        self.default_value = default_value
    
    def __repr__(self):
        return f'{self.property} : {self.range}'

    def __hash__(self):
        return hash((self.property))

    def __eq__(self, other):
        return (self.property) == (other.property)
            
class Role(Property):
    def __init__(self):
        props = [Confidence()]
        super().__init__(properties=props)

class Name(Property):
    def __init__(self):
        super().__init__()

class Alias(Property):
    def __init__(self,range=None):
        props = [Confidence()]
        super().__init__(range,props)
        
class HasPart(Property):
    def __init__(self,range=None):
        props = [Confidence()]
        super().__init__(range,props)

class HasSequence(Property):
    def __init__(self):
        super().__init__(String)

class HasCharacteristic(Property):
    def __init__(self):
        super().__init__()

class ConsistsOf(Property):
    def __init__(self,range=None):
        super().__init__(range)

class Direction(Property):
    def __init__(self,value):
        r = [Input(),Output()]
        super().__init__(r,default_value=value)

class Confidence(Property):
    def __init__(self):
        super().__init__(Integer,default_value=Literal(50))
    