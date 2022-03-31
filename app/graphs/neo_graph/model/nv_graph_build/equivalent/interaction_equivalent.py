from equivalent.abstract_equivalent import ConceptualEquivalent
from restriction import interaction_restriction as ir

class ActivationRoleEquivalent(ConceptualEquivalent):
    def __init__(self):
        restrictions = [ir.ActivationRoleRestriction()]
        super().__init__(restrictions)

class RepressionRoleEquivalent(ConceptualEquivalent):
    def __init__(self):
        restrictions = [ir.RepressionRoleRestriction()]
        super().__init__(restrictions)

class GeneticProductionRoleEquivalent(ConceptualEquivalent):
    def __init__(self):
        restrictions = [ir.GeneticProductionRoleRestriction()]
        super().__init__(restrictions)

class DegradationRoleEquivalent(ConceptualEquivalent):
    def __init__(self):
        restrictions = [ir.DegradationRoleRestriction()]
        super().__init__(restrictions)

class BindsRoleEquivalent(ConceptualEquivalent):
    def __init__(self):
        restrictions = [ir.BindsRoleRestriction()]
        super().__init__(restrictions)

class ConversionRoleEquivalent(ConceptualEquivalent):
    def __init__(self):
        restrictions = [ir.ConversionRoleRestriction()]
        super().__init__(restrictions)