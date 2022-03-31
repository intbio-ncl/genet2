from entities.abstract_entity import ConceptualEntity
from entities.abstract_entity import PhysicalEntity
from entities.reaction import Reaction
from equivalent import interaction_equivalent as ce
from restriction import interaction_recipes as ir
from property.property import ConsistsOf
from property import interactions as ins

class Interaction(ConceptualEntity):
    def __init__(self,properties=[],equivalents=[],restrictions=[]):
        if equivalents == []:
            equiv = []
        else:
            equiv = equivalents
        if restrictions == []:
            res = []
        else:
            res = restrictions
        p = properties + [ConsistsOf([Interaction,Reaction])]
        super().__init__(properties=p,
        equivalents=equiv,restrictions=res)

class Activation(Interaction):
    def __init__(self,properties=[],equivalents=[],restrictions=[]):
        if equivalents == []:
            equiv = [ce.ActivationRoleEquivalent()]
        else:
            equiv = equivalents
        if restrictions == []:
            res = [ir.ActivationRecipe()]
        else:
            res = restrictions
        
        p = properties + [ins.Activator(PhysicalEntity),
                          ins.Activated(PhysicalEntity)]
        super().__init__(properties=p,equivalents=equiv,restrictions=res)

class Repression(Interaction):
    def __init__(self,properties=[],equivalents=[],restrictions=[]):
        if equivalents == []:
            equiv = [ce.RepressionRoleEquivalent()]
        else:
            equiv = equivalents
        if restrictions == []:
            res = [ir.RepressionRecipe()]
        else:
            res = restrictions
        
        p = properties + [ins.Repressor(PhysicalEntity),
                          ins.Repressed(PhysicalEntity)]
        super().__init__(properties=p,equivalents=equiv,restrictions=res)

class GeneticProduction(Interaction):
    def __init__(self,properties=[],equivalents=[],restrictions=[]):
        if equivalents == []:
            equiv = [ce.GeneticProductionRoleEquivalent()]
        else:
            equiv = equivalents
        if restrictions == []:
            res = [ir.GeneticProductionRecipe()]
        else:
            res = restrictions
        super().__init__(properties=properties,
        equivalents=equiv,restrictions=res)


class Degradation(Interaction):
    def __init__(self,properties=[],equivalents=[],restrictions=[]):
        if equivalents == []:
            equiv = [ce.DegradationRoleEquivalent()]
        else:
            equiv = equivalents
        if restrictions == []:
            res = [ir.DegradationRecipe()]
        else:
            res = restrictions
        super().__init__(properties=properties,
        equivalents=equiv,restrictions=res)

class Binds(Interaction):
    def __init__(self,properties=[],equivalents=[],restrictions=[]):
        if equivalents == []:
            equiv = [ce.BindsRoleEquivalent()]
        else:
            equiv = equivalents
        if restrictions == []:
            res = [ir.BindsRecipe()]
        else:
            res = restrictions
        super().__init__(properties=properties,
        equivalents=equiv,restrictions=res)

class Conversion(Interaction):
    def __init__(self,properties=[],equivalents=[],restrictions=[]):
        if equivalents == []:
            equiv = [ce.ConversionRoleEquivalent()]
        else:
            equiv = equivalents
        if restrictions == []:
            res = [ir.ConversionRecipe()]
        else:
            res = restrictions
        super().__init__(properties=properties,
        equivalents=equiv,restrictions=res)
