from restriction.abstract_restriction import RoleRestriction
from restriction.abstract_restriction import CharacteristicRestriction
from identifiers import identifiers

class ConceptualCharacteristicRestriction(CharacteristicRestriction):
    def __init__(self):
        super().__init__(identifiers.roles.conceptual_entity)

class TranslationRoleRestriction(RoleRestriction):
    def __init__(self):
        values = [identifiers.roles.translation]
        super().__init__(values)

class TranscriptionRoleRestriction(RoleRestriction):
    def __init__(self):
        values = [identifiers.roles.transcription]
        super().__init__(values)

class DegradationRoleRestriction(RoleRestriction):
    def __init__(self):
        values = [identifiers.roles.degradation]
        super().__init__(values)

class NonCovBondingRoleRestriction(RoleRestriction):
    def __init__(self):
        values = [identifiers.roles.noncovalent_bonding]
        super().__init__(values)

class DissociationRoleRestriction(RoleRestriction):
    def __init__(self):
        values = [identifiers.roles.dissociation]
        super().__init__(values)

class HydrolysisRoleRestriction(RoleRestriction):
    def __init__(self):
        values = [identifiers.roles.hydrolysis]
        super().__init__(values)

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