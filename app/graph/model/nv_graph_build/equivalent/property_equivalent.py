from equivalent.abstract_equivalent import EquivalentProperty
from identifiers import identifiers

class ActivatorEquivalent(EquivalentProperty):
    def __init__(self):
        e = [identifiers.roles.stimulator]
        super().__init__(e)

class ActivatedEquivalent(EquivalentProperty):
    def __init__(self):
        e = [identifiers.roles.stimulated]
        super().__init__(e)

class RepressorEquivalent(EquivalentProperty):
    def __init__(self):
        e = [identifiers.roles.inhibitor]
        super().__init__(e)

class RepressedEquivalent(EquivalentProperty):
    def __init__(self):
        e = [identifiers.roles.inhibited]
        super().__init__(e)

class ReactantEquivalent(EquivalentProperty):
    def __init__(self):
        e = [identifiers.roles.reactant]
        super().__init__(e)

class InhibitorEquivalent(EquivalentProperty):
    def __init__(self):
        e = [identifiers.roles.inhibitor]
        super().__init__(e)

class StimulatorEquivalent(EquivalentProperty):
    def __init__(self):
        e = [identifiers.roles.stimulator]
        super().__init__(e)

class PromoterEquivalent(EquivalentProperty):
    def __init__(self):
        e = [identifiers.roles.participation_promoter]
        super().__init__(e)

class ModifierEquivalent(EquivalentProperty):
    def __init__(self):
        e = [identifiers.roles.modifier]
        super().__init__(e)

class ProductEquivalent(EquivalentProperty):
    def __init__(self):
        e = [identifiers.roles.product]
        super().__init__(e)

class InhibitedEquivalent(EquivalentProperty):
    def __init__(self):
        e = [identifiers.roles.inhibited]
        super().__init__(e)

class StimulatedEquivalent(EquivalentProperty):
    def __init__(self):
        e = [identifiers.roles.stimulated]
        super().__init__(e)

class ModifiedEquivalent(EquivalentProperty):
    def __init__(self):
        e = [identifiers.roles.modified]
        super().__init__(e)

class TemplateEquivalent(EquivalentProperty):
    def __init__(self):
        e = [identifiers.roles.template]
        super().__init__(e)

class PromoterEquivalent(EquivalentProperty):
    def __init__(self):
        e = [identifiers.roles.gp_promoter]
        super().__init__(e)