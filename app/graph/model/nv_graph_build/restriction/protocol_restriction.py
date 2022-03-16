from rdflib import OWL
from restriction.abstract_restriction import RoleRestriction
from restriction.abstract_restriction import SourceRestriction
from restriction.abstract_restriction import DestinationRestriction
from identifiers import identifiers

class ActionRestriction(RoleRestriction):
    def __init__(self):
        values = [identifiers.roles.action]
        super().__init__(values)

class ContainerRestriction(RoleRestriction):
    def __init__(self):
        values = [identifiers.roles.container]
        super().__init__(values)

class InstrumentRestriction(RoleRestriction):
    def __init__(self):
        values = [identifiers.roles.instrument]
        super().__init__(values)

class PipetteRestriction(RoleRestriction):
    def __init__(self):
        values = [identifiers.roles.pipette]
        super().__init__(values)

class ProtocolRestriction(RoleRestriction):
    def __init__(self):
        values = [identifiers.roles.protocol]
        super().__init__(values)

class ApparatusRestriction(RoleRestriction):
    def __init__(self):
        values = [identifiers.roles.external_machine]
        super().__init__(values)

class WellRestriction(RoleRestriction):
    def __init__(self):
        values = [identifiers.roles.well]
        super().__init__(values)


class ZeroSourceRestriction(SourceRestriction):
    def __init__(self):
        super().__init__(OWL.cardinality,0)

class OneSourceRestriction(SourceRestriction):
    def __init__(self):
        super().__init__(OWL.cardinality,1)

class ManySourceRestriction(SourceRestriction):
    def __init__(self):
        super().__init__(OWL.minCardinality,2)
    
class ZeroDestinationRestriction(DestinationRestriction):
    def __init__(self):
        super().__init__(OWL.cardinality,0)

class OneDestinationRestriction(DestinationRestriction):
    def __init__(self):
        super().__init__(OWL.cardinality,1)

class ManyDestinationRestriction(DestinationRestriction):
    def __init__(self):
        super().__init__(OWL.minCardinality,2)