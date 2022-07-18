from property.property import Property
from datatype.datatype import Integer

class HasInstrument(Property):
    def __init__(self,range=None):
        super().__init__(range)

class HasApparatus(Property):
    def __init__(self,range=None):
        super().__init__(range)

class HasContainer(Property):
    def __init__(self,range=None):
        super().__init__(range)

class Actions(Property):
    def __init__(self,range=None):
        super().__init__(range=range)

class Well(Property):
    def __init__(self,range=None):
        super().__init__(range=range)

class HasSubProtocol(Property):
    def __init__(self,range=None):
        super().__init__(range=range)

class UsesApparatus(Property):
    def __init__(self,range=None):
        super().__init__(range)

class UsesInstrument(Property):
    def __init__(self,range=None):
        super().__init__(range)

class MayUseApparatus(Property):
    def __init__(self,range=None,default_value=None):
        super().__init__(range,default_value=default_value)

class MayUseInstrument(Property):
    def __init__(self,range=None,default_value=None):
        super().__init__(range,default_value=default_value)

class ColNum(Property):
    def __init__(self,range=None,default_value=None):
        super().__init__(range,default_value=default_value)

class RowNum(Property):
    def __init__(self,range=None,default_value=None):
        super().__init__(range,default_value=default_value)