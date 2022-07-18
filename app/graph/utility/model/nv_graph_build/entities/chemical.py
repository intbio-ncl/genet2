from entities.abstract_entity import PhysicalEntity
from equivalent import physcial_equivalent as pe

# -------------- Small Molecule --------------
class SmallMolecule(PhysicalEntity):
    def __init__(self,equivalents=[]):
        if equivalents == []:
            r = [pe.SmallMoleculeRoleEquivalent()]
        else:
            r = equivalents
        super().__init__(equivalents=r)  

class Effector(SmallMolecule):
    def __init__(self,equivalents=[]):
        if equivalents == []:
            r = [pe.EffectorRoleEquivalent()]
        else:
            r = equivalents
        super().__init__(equivalents=r)