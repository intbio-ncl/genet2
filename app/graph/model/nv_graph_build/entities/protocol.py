from entities.abstract_entity import ConceptualEntity
from entities.instrument import Instrument
from entities.apparatus import Apparatus
from entities.container import Container
from entities.action import Action
from property import protocols as pp
from equivalent import protocol_equivalent as pe
from equivalent import abstract_equivalent as ae

class Protocol(ConceptualEntity):
    def __init__(self,properties=[],equivalents=[],restrictions=[]):
        if equivalents == []:
            e = [pe.ProtocolEquivalent()]
        else:
            e = equivalents
        p = [
            pp.HasSubProtocol(Protocol),
            pp.Actions(Action),
            pp.HasContainer(Container),
            pp.HasInstrument(Instrument),
            pp.HasApparatus(Apparatus)
        ] + properties
        super().__init__(properties=p,equivalents=e,
                        restrictions=restrictions)

class MasterProtocol(Protocol):
    def __init__(self,properties=[],equivalents=[],restrictions=[]):
        name = self.__class__.__name__.split("Protocol")[0]
        e = equivalents + [ae.NameEquivalentClass(name)]
        super().__init__(properties=properties,equivalents=e,
                        restrictions=restrictions)

class AssemblyProtocol(Protocol):
    def __init__(self,properties=[],equivalents=[],restrictions=[]):
        name = self.__class__.__name__.split("Protocol")[0]
        e = equivalents + [ae.NameEquivalentClass(name)]
        super().__init__(properties=properties,equivalents=e,
                        restrictions=restrictions)

class RestrictionProtocol(Protocol):
    def __init__(self,properties=[],equivalents=[],restrictions=[]):
        name = self.__class__.__name__.split("Protocol")[0]
        e = equivalents + [ae.NameEquivalentClass(name)]
        super().__init__(properties=properties,equivalents=e,
                        restrictions=restrictions)

class PurificationProtocol(Protocol):
    def __init__(self,properties=[],equivalents=[],restrictions=[]):
        name = self.__class__.__name__.split("Protocol")[0]
        e = equivalents + [ae.NameEquivalentClass(name)]
        super().__init__(properties=properties,equivalents=e,
                        restrictions=restrictions)

class TransformationProtocol(Protocol):
    def __init__(self,properties=[],equivalents=[],restrictions=[]):
        name = self.__class__.__name__.split("Protocol")[0]
        e = equivalents + [ae.NameEquivalentClass(name)]
        super().__init__(properties=properties,equivalents=e,
                        restrictions=restrictions)

class PrepareCellsProtocol(Protocol):
    def __init__(self,properties=[],equivalents=[],restrictions=[]):
        name = self.__class__.__name__.split("Protocol")[0]
        e = equivalents + [ae.NameEquivalentClass(name)]
        super().__init__(properties=properties,equivalents=e,
                        restrictions=restrictions)

class HeatShockProtocol(Protocol):
    def __init__(self,properties=[],equivalents=[],restrictions=[]):
        name = self.__class__.__name__.split("Protocol")[0]
        e = equivalents + [ae.NameEquivalentClass(name)]
        super().__init__(properties=properties,equivalents=e,
                        restrictions=restrictions)

class OutGrowthProtocol(Protocol):
    def __init__(self,properties=[],equivalents=[],restrictions=[]):
        name = self.__class__.__name__.split("Protocol")[0]
        e = equivalents + [ae.NameEquivalentClass(name)]
        super().__init__(properties=properties,equivalents=e,
                        restrictions=restrictions)

class ValidationProtocol(Protocol):
    def __init__(self,properties=[],equivalents=[],restrictions=[]):
        name = self.__class__.__name__.split("Protocol")[0]
        e = equivalents + [ae.NameEquivalentClass(name)]
        super().__init__(properties=properties,equivalents=e,
                        restrictions=restrictions)
class ColonyProtocol(Protocol):
    def __init__(self,properties=[],equivalents=[],restrictions=[]):
        name = self.__class__.__name__.split("Protocol")[0]
        e = equivalents + [ae.NameEquivalentClass(name)]
        super().__init__(properties=properties,equivalents=e,
                        restrictions=restrictions)

class SequencingProtocol(Protocol):
    def __init__(self,properties=[],equivalents=[],restrictions=[]):
        name = self.__class__.__name__.split("Protocol")[0]
        e = equivalents + [ae.NameEquivalentClass(name)]
        super().__init__(properties=properties,equivalents=e,
                        restrictions=restrictions)

class LigationProtocol(Protocol):
    def __init__(self,properties=[],equivalents=[],restrictions=[]):
        name = self.__class__.__name__.split("Protocol")[0]
        e = equivalents + [ae.NameEquivalentClass(name)]
        super().__init__(properties=properties,equivalents=e,
                        restrictions=restrictions)

class ColonyPCRProtocol(Protocol):
    def __init__(self,properties=[],equivalents=[],restrictions=[]):
        name = self.__class__.__name__.split("Protocol")[0]
        e = equivalents + [ae.NameEquivalentClass(name)]
        super().__init__(properties=properties,equivalents=e,
                        restrictions=restrictions)