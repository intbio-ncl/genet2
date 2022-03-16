from entities import reaction
from annotation.annotation import Recipe

class ActivationRecipe(Recipe):
    def __init__(self):
        recipe = [reaction.NonCovalentBonding()]
        super().__init__(recipe)

class RepressionRecipe(Recipe):
    def __init__(self):
        recipe = [reaction.NonCovalentBonding()]
        super().__init__(recipe)

class GeneticProductionRecipe(Recipe):
    def __init__(self):
        recipe = [reaction.Transcription(),
                  reaction.Translation()]
        super().__init__(recipe)

class DegradationRecipe(Recipe):
    def __init__(self):
        recipe = [reaction.NonCovalentBonding()]
        super().__init__(recipe)

class BindsRecipe(Recipe):
    def __init__(self):
        recipe = [reaction.NonCovalentBonding()]
        super().__init__(recipe)
        
class ConversionRecipe(Recipe):
    def __init__(self):
        recipe = [reaction.BiochemicalReaction()]
        super().__init__(recipe)