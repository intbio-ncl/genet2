from rdflib import Literal
from restriction.abstract_restriction import NameRestriction
from restriction.physcial_restriction import PhyscialCharacteristicRestriction
from restriction.conceptual_restriction import ConceptualCharacteristicRestriction

class EquivalentClass:
    def __init__(self,restrictions=[]):
        self.restrictions = restrictions

class EquivalentProperty:
    def __init__(self,equivalents):
        self.equivalents = equivalents

class PhysicalEquivalent(EquivalentClass):
    def __init__(self,restrictions=[]):
        if restrictions == []:
            r = [PhyscialCharacteristicRestriction()]
        else:
            r = restrictions
        super().__init__(r)
        
class ConceptualEquivalent(EquivalentClass):
    def __init__(self,restrictions=[]):
        if restrictions == []:
            r = [ConceptualCharacteristicRestriction()]
        else:
            r = restrictions
        super().__init__(r)

class NameEquivalentClass(EquivalentClass):
    def __init__(self, names):
        if not isinstance(names,list):
            names = [names]
        r = [NameRestriction(names)]
        super().__init__(restrictions=r)

class NameEquivalentProperty(EquivalentProperty):
    def __init__(self, names):
        if not isinstance(names,list):
            names = [names]
        names = [Literal(n) for n in names]
        super().__init__(names)