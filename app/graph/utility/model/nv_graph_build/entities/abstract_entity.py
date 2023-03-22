from rdflib import URIRef
from identifiers import identifiers
from equivalent.abstract_equivalent import PhysicalEquivalent
from equivalent.abstract_equivalent import ConceptualEquivalent
from property.property import Alias
default_properties = [Alias]


class Entity:
    def __init__(self, disjoint=False, properties=[], equivalents=[], restrictions=[]):
        class_name = self.__class__.__name__
        self.uri = URIRef(identifiers.namespaces.nv + class_name)
        self.disjoint = disjoint
        self.properties = [p(Entity) for p in default_properties] + properties
        self.equivalents = equivalents
        self.restrictions = restrictions

    @classmethod
    def uri(cls):
        return URIRef(identifiers.namespaces.nv + cls.__name__)

class PhysicalEntity(Entity):
    def __init__(self, disjoint=True, properties=[], equivalents=[], restrictions=[]):
        if equivalents == []:
            equiv = [PhysicalEquivalent()]
        else:
            equiv = equivalents
        super().__init__(disjoint, properties=properties,
                         equivalents=equiv, restrictions=restrictions)

class ConceptualEntity(Entity):
    def __init__(self, disjoint=True, properties=[], equivalents=[], restrictions=[]):
        if equivalents == []:
            equiv = [ConceptualEquivalent()]
        else:
            equiv = equivalents
        super().__init__(disjoint, properties=properties,
                         equivalents=equiv, restrictions=restrictions)
