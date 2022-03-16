class Annotation:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

class Recipe(Annotation):
    def __init__(self,recipe):
        super().__init__(recipe=recipe)
        

