from restriction.abstract_restriction import RoleRestriction
from identifiers import identifiers

class ActivationRoleRestriction(RoleRestriction):
    def __init__(self):
        values = [identifiers.roles.stimulation]
        super().__init__(values)

class RepressionRoleRestriction(RoleRestriction):
    def __init__(self):
        values = [identifiers.roles.inhibition]
        super().__init__(values)

class GeneticProductionRoleRestriction(RoleRestriction):
    def __init__(self):
        values = [identifiers.roles.genetic_production]
        super().__init__(values)

class DegradationRoleRestriction(RoleRestriction):
    def __init__(self):
        values = [identifiers.roles.degradation]
        super().__init__(values)

class BindsRoleRestriction(RoleRestriction):
    def __init__(self):
        values = [identifiers.roles.noncovalent_bonding]
        super().__init__(values)

class ConversionRoleRestriction(RoleRestriction):
    def __init__(self):
        values = [identifiers.roles.biochemical_reaction]
        super().__init__(values)