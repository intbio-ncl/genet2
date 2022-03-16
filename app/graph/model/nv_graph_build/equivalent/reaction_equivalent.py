from equivalent.abstract_equivalent import ConceptualEquivalent
from restriction import reaction_restriction as rr

class TranslationRoleEquivalent(ConceptualEquivalent):
    def __init__(self):
        restrictions = [rr.TranslationRoleRestriction()]
        super().__init__(restrictions)

class TranscriptionRoleEquivalent(ConceptualEquivalent):
    def __init__(self):
        restrictions = [rr.TranscriptionRoleRestriction()]
        super().__init__(restrictions)

class NonCovBondingRoleEquivalent(ConceptualEquivalent):
    def __init__(self):
        restrictions = [rr.NonCovBondingRoleRestriction()]
        super().__init__(restrictions)

class DissociationRoleEquivalent(ConceptualEquivalent):
    def __init__(self):
        restrictions = [rr.DissociationRoleRestriction()]
        super().__init__(restrictions)

class HydrolysisRoleEquivalent(ConceptualEquivalent):
    def __init__(self):
        restrictions = [rr.HydrolysisRoleRestriction()]
        super().__init__(restrictions)

class BiochemicalReactionRoleEquivalent(ConceptualEquivalent):
    def __init__(self):
        restrictions = [rr.BiochemicalReactionRoleRestriction()]
        super().__init__(restrictions)