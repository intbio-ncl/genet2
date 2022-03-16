from restriction.abstract_restriction import ActionRecipeRestriction
from annotation import action_recipes as ar
import entities.action

class ActionRecipe(ActionRecipeRestriction):
    def __init__(self,recipe):
        i_range = [entities.action.Action]
        super().__init__(recipe,i_range)
        
class TransferRecipe(ActionRecipe):
    def __init__(self):
        recipe = ar.TransferRecipe()
        super().__init__(recipe)

