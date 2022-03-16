from equivalent.abstract_equivalent import PhysicalEquivalent
from restriction import physcial_restriction as pr

class DNARoleEquivalent(PhysicalEquivalent):
    def __init__(self):
        restrictions = [pr.DNARoleRestriction()]
        super().__init__(restrictions)

class PromoterRoleEquivalent(PhysicalEquivalent):
    def __init__(self):
        restrictions = [pr.PromoterRoleRestriction()]
        super().__init__(restrictions)

class RBSRoleEquivalent(PhysicalEquivalent):
    def __init__(self):
        restrictions = [pr.RBSRoleRestriction()]
        super().__init__(restrictions)

class CDSRoleEquivalent(PhysicalEquivalent):
    def __init__(self):
        restrictions = [pr.CDSRoleRestriction()]
        super().__init__(restrictions)

class TerminatorRoleEquivalent(PhysicalEquivalent):
    def __init__(self):
        restrictions = [pr.TerminatorRoleRestriction()]
        super().__init__(restrictions)

class GeneRoleEquivalent(PhysicalEquivalent):
    def __init__(self):
        restrictions = [pr.GeneRoleRestriction()]
        super().__init__(restrictions)

class OperatorRoleEquivalent(PhysicalEquivalent):
    def __init__(self):
        restrictions = [pr.OperatorRoleRestriction()]
        super().__init__(restrictions)

class EngineeredRegionRoleEquivalent(PhysicalEquivalent):
    def __init__(self):
        restrictions = [pr.EngineeredGeneRoleRestriction()]
        super().__init__(restrictions) 

class ComplexRoleEquivalent(PhysicalEquivalent):
    def __init__(self):
        restrictions = [pr.ComplexRoleRestriction()]
        super().__init__(restrictions)

class ProteinRoleEquivalent(PhysicalEquivalent):
    def __init__(self):
        restrictions = [pr.ProteinRoleRestriction()]
        super().__init__(restrictions)

class TranscriptionFactorRoleEquivalent(PhysicalEquivalent):
    def __init__(self):
        restrictions = [pr.TranscriptionFactorRoleRestriction()]
        super().__init__(restrictions)  

class EngineeredTagRoleEquivalent(PhysicalEquivalent):
    def __init__(self):
        restrictions = [pr.EngineeredGeneRoleRestriction()]
        super().__init__(restrictions)

class StartCodonRoleEquivalent(PhysicalEquivalent):
    def __init__(self):
        restrictions = [pr.StartCodonRoleRestriction()]
        super().__init__(restrictions)

class TagRoleEquivalent(PhysicalEquivalent):
    def __init__(self):
        restrictions = [pr.TagRoleRestriction()]
        super().__init__(restrictions)

class NonCovBindingSiteRoleEquivalent(PhysicalEquivalent):
    def __init__(self):
        restrictions = [pr.NonCovBindingSiteRoleRestriction()]
        super().__init__(restrictions)

class EngineeredGeneRoleEquivalent(PhysicalEquivalent):
    def __init__(self):
        restrictions = [pr.EngineeredGeneRoleRestriction()]
        super().__init__(restrictions)
        
class RNARoleEquivalent(PhysicalEquivalent):
    def __init__(self):
        restrictions = [pr.RNARegionRoleRestriction()]
        super().__init__(restrictions)

class mRNARoleEquivalent(PhysicalEquivalent):
    def __init__(self):
        restrictions = [pr.mRNARoleRestriction()]
        super().__init__(restrictions)

class sgRNARoleEquivalent(PhysicalEquivalent):
    def __init__(self):
        restrictions = [pr.sgRNARoleRestriction()]
        super().__init__(restrictions)

class SmallMoleculeRoleEquivalent(PhysicalEquivalent):
    def __init__(self):
        restrictions = [pr.SmallMoleculeRoleRestriction()]
        super().__init__(restrictions)

class EffectorRoleEquivalent(PhysicalEquivalent):
    def __init__(self):
        restrictions = [pr.EffectorRoleRestriction()]
        super().__init__(restrictions)