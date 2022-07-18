from property.property import Property
from property.property import Direction
from datatype.datatype import Input,Output
from equivalent import property_equivalent as pe

class InteractionProperty(Property):
    def __init__(self,range,properties=[],equivalents=[]):
        super().__init__(range,properties=properties,equivalents=equivalents)

class Activator(InteractionProperty):
    def __init__(self,range=None):
        p = [Direction(Input())]
        e = [pe.ActivatorEquivalent()]
        super().__init__(range,p,e)

class Activated(InteractionProperty):
    def __init__(self,range=None):
        p = [Direction(Output())]
        e = [pe.ActivatedEquivalent()]
        super().__init__(range,p,e)

class Repressor(InteractionProperty):
    def __init__(self,range=None):
        p = [Direction(Input())]
        e = [pe.RepressorEquivalent()]
        super().__init__(range,p,e)

class Repressed(InteractionProperty):
    def __init__(self,range=None):
        p = [Direction(Output())]
        e = [pe.RepressedEquivalent()]
        super().__init__(range,p,e)
