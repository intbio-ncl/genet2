from property.property import Property
from property.property import Direction
from datatype.datatype import Input,Output
from equivalent import property_equivalent as pe
from property.property import Confidence

class ReactionProperty(Property):
    def __init__(self,range,properties=[],equivalents=[]):
        p = [Confidence()] + properties
        super().__init__(range,properties=p,equivalents=equivalents)

class Reactant(ReactionProperty):
    def __init__(self,range=None):
        p = [Direction(Input())]
        e = [pe.ReactantEquivalent(),
             pe.InhibitorEquivalent(),
             pe.StimulatorEquivalent(),
             pe.PromoterEquivalent()]
        super().__init__(range,p,e)

class Product(ReactionProperty):
    def __init__(self,range=None):
        p = [Direction(Output())]
        e = [pe.ProductEquivalent(),
             pe.InhibitedEquivalent(),
             pe.StimulatedEquivalent(),
             pe.ModifiedEquivalent()]
        super().__init__(range,p,e)

class Template(ReactionProperty):
    def __init__(self,range=None):
        '''
        Note: Promoter is just to appease SBOL it doesn't make much sense.
        '''
        p = [Direction(Input())]
        e = [pe.TemplateEquivalent(),
            pe.PromoterEquivalent()]
        super().__init__(range,p,e)


class Modifier(ReactionProperty):
    def __init__(self,range=None):
        p = [Direction(Input())]
        e = [pe.ModifierEquivalent()]
        super().__init__(range,p,e)
