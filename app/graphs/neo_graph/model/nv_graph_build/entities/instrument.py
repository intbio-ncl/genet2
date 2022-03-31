from entities.abstract_entity import PhysicalEntity
from equivalent import protocol_equivalent as pe

class Instrument(PhysicalEntity):
    def __init__(self,properties=[],equivalents=[],restrictions=[]):
        if equivalents == []:
            e = [pe.InstrumentEquivalent()]
        else:
            e = equivalents
        super().__init__(properties=properties,equivalents=e,
                        restrictions=restrictions)

class Pipette(Instrument): # Source
    def __init__(self,properties=[],equivalents=[],restrictions=[]):
        e = equivalents + [pe.PipetteEquivalent()]
        p = properties
        super().__init__(properties=p,equivalents=e,
                        restrictions=restrictions)