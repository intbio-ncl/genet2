from rdflib import Literal
from rdflib.extras.infixowl import Property
from property.property import Property
from property.property import Role
from property.property import Name
from property.property import HasCharacteristic
from property.property import ConsistsOf
from property.protocols import Actions
from property.actions import Source
from property.actions import Destination

class Restriction:
    def __init__(self,property):
        if not isinstance(property,Property):
            property = Property(property)
        self.property = property

class ValueRestriction(Restriction):
    def __init__(self,property,values):
        super().__init__(property)
        if not isinstance(values,(list,tuple,set)):
            values = [values]
        self.values = values

class CardinalityRestriction(Restriction):
    def __init__(self,property,constraint,value):
        super().__init__(property)
        self.constraint = constraint
        self.value = Literal(value)

class RoleRestriction(ValueRestriction):
    def __init__(self,values):
        super().__init__(Role(),values)

class CharacteristicRestriction(ValueRestriction):
    def __init__(self,values):
        super().__init__(HasCharacteristic(),values)

class RecipeRestriction(ValueRestriction):
    def __init__(self,recipe,r_range):
        super().__init__(ConsistsOf(r_range),recipe)

class ActionRecipeRestriction(ValueRestriction):
    def __init__(self,recipe,r_range):
        super().__init__(Actions(r_range),recipe)

class SourceRestriction(CardinalityRestriction):
    def __init__(self,constraint,value):
        super().__init__(Source(),constraint,value)

class DestinationRestriction(CardinalityRestriction):
    def __init__(self,constraint,value):
        super().__init__(Destination(),constraint,value)

class NameRestriction(ValueRestriction):
    def __init__(self,names):
        names = [Literal(n) for n in names]
        super().__init__(Name(),names)