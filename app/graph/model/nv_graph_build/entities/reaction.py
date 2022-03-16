from entities.abstract_entity import ConceptualEntity,PhysicalEntity
from equivalent import reaction_equivalent as ce
from property import reactions


class Reaction(ConceptualEntity):
    def __init__(self,equivalents=[],properties=[]):
        if equivalents == []:
            r = []
        else:
            r = equivalents
        super().__init__(equivalents=r,properties=properties)

class Transcription(Reaction):
    def __init__(self,equivalents=[]):
        if equivalents == []:
            r = [ce.TranscriptionRoleEquivalent()]
        else:
            r = equivalents
        p = [reactions.Template(PhysicalEntity),
            reactions.Product(PhysicalEntity)]
        super().__init__(equivalents=r,properties=p)

class Translation(Reaction):
    def __init__(self,equivalents=[]):
        if equivalents == []:
            r = [ce.TranslationRoleEquivalent()]
        else:
            r = equivalents
        p = [reactions.Template(PhysicalEntity),
            reactions.Product(PhysicalEntity)]
        super().__init__(equivalents=r,properties=p)

class NonCovalentBonding(Reaction):
    def __init__(self,equivalents=[]):
        if equivalents == []:
            r = [ce.NonCovBondingRoleEquivalent()]
        else:
            r = equivalents
        p = [reactions.Reactant(PhysicalEntity),
            reactions.Product(PhysicalEntity)]
        super().__init__(equivalents=r,properties=p)

class Dissociation(Reaction):
    def __init__(self,equivalents=[],properties=[]):
        if equivalents == []:
            r = [ce.DissociationRoleEquivalent()]
        else:
            r = equivalents
        p = [reactions.Reactant(PhysicalEntity),
            reactions.Product(PhysicalEntity)]
        super().__init__(equivalents=r,properties=p)

class Hydrolysis(Dissociation):
    def __init__(self,equivalents=[]):
        if equivalents == []:
            r = [ce.HydrolysisRoleEquivalent()]
        else:
            r = equivalents
        p = [reactions.Reactant(PhysicalEntity),
            reactions.Product(PhysicalEntity)]
        super().__init__(equivalents=r,properties=p)

class BiochemicalReaction(Reaction):
    def __init__(self,equivalents=[]):
        if equivalents == []:
            r = [ce.BiochemicalReactionRoleEquivalent()]
        else:
            r = equivalents
        p = [reactions.Reactant(PhysicalEntity),
             reactions.Modifier(PhysicalEntity),
            reactions.Product(PhysicalEntity)]
        super().__init__(equivalents=r,properties=p)
