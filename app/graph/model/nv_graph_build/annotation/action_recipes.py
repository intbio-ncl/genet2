
from annotation.annotation import Recipe
import entities.action

class TransferRecipe(Recipe):
    def __init__(self):
        recipe = [entities.action.Extract(),
                  entities.action.Dispense()]
        super().__init__(recipe)



        