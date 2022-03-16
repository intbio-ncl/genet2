from restriction.abstract_restriction import RoleRestriction
from identifiers import identifiers

class TranslationRoleRestriction(RoleRestriction):
    def __init__(self):
        values = [identifiers.roles.translation]
        super().__init__(values)

class TranscriptionRoleRestriction(RoleRestriction):
    def __init__(self):
        values = [identifiers.roles.transcription]
        super().__init__(values)

class NonCovBondingRoleRestriction(RoleRestriction):
    def __init__(self):
        values = [identifiers.roles.association]
        super().__init__(values)

class DissociationRoleRestriction(RoleRestriction):
    def __init__(self):
        values = [identifiers.roles.dissociation]
        super().__init__(values)

class HydrolysisRoleRestriction(RoleRestriction):
    def __init__(self):
        values = [identifiers.roles.hydrolysis]
        super().__init__(values)

class BiochemicalReactionRoleRestriction(RoleRestriction):
    def __init__(self):
        values = [identifiers.roles.biochemical_reaction]
        super().__init__(values)