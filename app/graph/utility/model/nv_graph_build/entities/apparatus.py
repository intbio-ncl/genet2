from entities.abstract_entity import PhysicalEntity
from equivalent import protocol_equivalent as pe
from equivalent import abstract_equivalent as ae

class Apparatus(PhysicalEntity):
    def __init__(self,properties=[],equivalents=[],restrictions=[]):
        if equivalents == []:
            e = [pe.ApparatusEquivalent()]
        else:
            e = equivalents
        super().__init__(properties=properties,equivalents=e,
                        restrictions=restrictions)

class Thermocycler(PhysicalEntity):
    def __init__(self,properties=[],equivalents=[],restrictions=[]):
        e = equivalents + [ae.NameEquivalentClass(self.__class__.__name__)]
        super().__init__(properties=properties,equivalents=e,
                        restrictions=restrictions)

class Centrifuge(PhysicalEntity):
    def __init__(self,properties=[],equivalents=[],restrictions=[]):
        e = equivalents + [ae.NameEquivalentClass(self.__class__.__name__)]
        super().__init__(properties=properties,equivalents=e,
                        restrictions=restrictions)

class Incubator(PhysicalEntity):
    def __init__(self,properties=[],equivalents=[],restrictions=[]):
        e = equivalents + [ae.NameEquivalentClass(self.__class__.__name__)]
        super().__init__(properties=properties,equivalents=e,
                        restrictions=restrictions)


