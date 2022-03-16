from entities.abstract_entity import PhysicalEntity
from equivalent import physcial_equivalent as pe

class Protein(PhysicalEntity):
    def __init__(self,equivalents=[]):
        if equivalents == []:
            r = [pe.ProteinRoleEquivalent()]
        else:
            r = equivalents
        super().__init__(equivalents=r)

class TranscriptionFactor(Protein):
    def __init__(self,equivalents=[]):
        if equivalents == []:
            r = [pe.TranscriptionFactorRoleEquivalent()]
        else:
            r = equivalents
        super().__init__(equivalents=r)