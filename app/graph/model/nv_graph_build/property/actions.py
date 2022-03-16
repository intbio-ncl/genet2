from property.property import Property
from datatype.datatype import Integer,String
from equivalent import abstract_equivalent as ae

class Source(Property):
    def __init__(self,range=None):
        equivs = [self.__class__.__name__.lower(),"reagent_source"]
        e = [ae.NameEquivalentProperty(equivs)]
        super().__init__(range,equivalents=e)

class Destination(Property):
    def __init__(self,range=None):
        e = [ae.NameEquivalentProperty(self.__class__.__name__.lower())]
        super().__init__(range,equivalents=e)

class Volume(Property):
    def __init__(self):
        e = [ae.NameEquivalentProperty(self.__class__.__name__.lower())]
        super().__init__(Integer,equivalents=e)

class Object(Property):
    def __init__(self,range=None):
        e = [ae.NameEquivalentProperty(self.__class__.__name__.lower())]
        super().__init__(range,equivalents=e)

class Speed(Property):
    def __init__(self):
        equivs = [self.__class__.__name__.lower(),"acceleration"]
        e = [ae.NameEquivalentProperty(equivs)]
        super().__init__(String,equivalents=e)

class Duration(Property):
    def __init__(self):
        e = [ae.NameEquivalentProperty(self.__class__.__name__.lower())]
        super().__init__(String,equivalents=e)

class Duration(Property):
    def __init__(self):
        e = [ae.NameEquivalentProperty(self.__class__.__name__.lower())]
        super().__init__(String,equivalents=e)

class Temperature(Property):
    def __init__(self):
        e = [ae.NameEquivalentProperty(self.__class__.__name__.lower())]
        super().__init__(String,equivalents=e)

class Cycles(Property):
    def __init__(self):
        e = [ae.NameEquivalentProperty(self.__class__.__name__.lower())]
        super().__init__(Integer,equivalents=e)