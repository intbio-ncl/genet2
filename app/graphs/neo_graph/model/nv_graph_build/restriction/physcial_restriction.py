from restriction.abstract_restriction import RoleRestriction
from restriction.abstract_restriction import CharacteristicRestriction
from identifiers import identifiers

class PhyscialCharacteristicRestriction(CharacteristicRestriction):
    def __init__(self):
        super().__init__(identifiers.roles.physical_entity)

class DNARoleRestriction(RoleRestriction):
    def __init__(self):
        values = [identifiers.roles.DNA,
                  identifiers.roles.DNARegion]
        super().__init__(values)

class PromoterRoleRestriction(RoleRestriction):
    def __init__(self):
        super().__init__(identifiers.roles.promoter)

class RBSRoleRestriction(RoleRestriction):
    def __init__(self):
        super().__init__(identifiers.roles.rbs)  

class CDSRoleRestriction(RoleRestriction):
    def __init__(self):
        super().__init__(identifiers.roles.cds)  

class TerminatorRoleRestriction(RoleRestriction):
    def __init__(self):
        super().__init__(identifiers.roles.terminator)  

class GeneRoleRestriction(RoleRestriction):
    def __init__(self):
        super().__init__(identifiers.roles.gene)  

class OperatorRoleRestriction(RoleRestriction):
    def __init__(self):
        super().__init__(identifiers.roles.operator)  

class EngineeredRegionRoleRestriction(RoleRestriction):
    def __init__(self):
        super().__init__(identifiers.roles.engineeredRegion)  

class ComplexRoleRestriction(RoleRestriction):
    def __init__(self):
        super().__init__(identifiers.roles.complex)  

class ProteinRoleRestriction(RoleRestriction):
    def __init__(self):
        super().__init__(identifiers.roles.protein)  

class TranscriptionFactorRoleRestriction(RoleRestriction):
    def __init__(self):
        super().__init__(identifiers.roles.transcriptionFactor)  

class EngineeredTagRoleRestriction(RoleRestriction):
    def __init__(self):
        super().__init__(identifiers.roles.engineeredTag)  

class StartCodonRoleRestriction(RoleRestriction):
    def __init__(self):
        super().__init__(identifiers.roles.startCodon)  

class TagRoleRestriction(RoleRestriction):
    def __init__(self):
        super().__init__(identifiers.roles.tag)  

class NonCovBindingSiteRoleRestriction(RoleRestriction):
    def __init__(self):
        super().__init__(identifiers.roles.nonCovBindingSite)  

class EngineeredGeneRoleRestriction(RoleRestriction):
    def __init__(self):
        super().__init__(identifiers.roles.engineeredGene)  
        
class RNARoleRestriction(RoleRestriction):
    def __init__(self):
        values = [identifiers.roles.RNA,
                  identifiers.roles.RNARegion]
        super().__init__(values)  

class RNARegionRoleRestriction(RoleRestriction):
    def __init__(self):
        super().__init__(identifiers.roles.RNARegion)

class mRNARoleRestriction(RoleRestriction):
    def __init__(self):
        super().__init__(identifiers.roles.mRNA)  

class sgRNARoleRestriction(RoleRestriction):
    def __init__(self):
        super().__init__(identifiers.roles.sgRNA)  

class SmallMoleculeRoleRestriction(RoleRestriction):
    def __init__(self):
        super().__init__(identifiers.roles.smallMolecule)  

class EffectorRoleRestriction(RoleRestriction):
    def __init__(self):
        super().__init__(identifiers.roles.effector)