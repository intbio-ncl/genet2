from restriction.abstract_restriction import RecipeRestriction
from annotation import interaction_recipes as ir
import entities.interaction
import entities.reaction

class InteractionRecipe(RecipeRestriction):
    def __init__(self,recipe):
        i_range = [entities.interaction.Interaction,
                   entities.reaction.Reaction]
        super().__init__(recipe,i_range)

class ActivationRecipe(InteractionRecipe):
    def __init__(self):
        recipe = ir.ActivationRecipe()
        super().__init__(recipe)

class RepressionRecipe(InteractionRecipe):
    def __init__(self):
        recipe = ir.RepressionRecipe()
        super().__init__(recipe)

class GeneticProductionRecipe(InteractionRecipe):
    def __init__(self):
        recipe = ir.GeneticProductionRecipe()
        super().__init__(recipe)

class DegradationRecipe(InteractionRecipe):
    def __init__(self):
        recipe = ir.DegradationRecipe()
        super().__init__(recipe)

class BindsRecipe(InteractionRecipe):
    def __init__(self):
        recipe = ir.BindsRecipe()
        super().__init__(recipe)

class ConversionRecipe(InteractionRecipe):
    def __init__(self):
        recipe = ir.ConversionRecipe()
        super().__init__(recipe)