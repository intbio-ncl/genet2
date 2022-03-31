from entities.abstract_entity import ConceptualEntity
from entities.instrument import Instrument,Pipette
from entities.apparatus import Apparatus,Thermocycler,Centrifuge,Incubator
from entities.container import Well,Container
from property import protocols as pp
from property import actions as ap
from equivalent import abstract_equivalent as ae
from equivalent import protocol_equivalent as pe
from restriction import action_recipes as ar


class Action(ConceptualEntity):
    def __init__(self,properties=[],equivalents=[],restrictions=[]):
        if equivalents == []:
            e = [pe.ActionEquivalent()]
        else:
            e = equivalents
        p = [pp.Actions(Action),
            pp.UsesApparatus(Apparatus),
            pp.UsesInstrument(Instrument)] + properties
        super().__init__(properties=p,equivalents=e,
                        restrictions=restrictions)

class Restriction(Action):
    def __init__(self,properties=[],equivalents=[],restrictions=[]):
        name = self.__class__.__name__
        e = equivalents + [ae.NameEquivalentClass(name)]
        p = properties + [pp.MayUseInstrument(default_value=Pipette),
                          pp.MayUseApparatus(default_value=Thermocycler),
                          pp.MayUseApparatus(default_value=Centrifuge),
                          pp.MayUseApparatus(default_value=Incubator)]
        super().__init__(properties=p,equivalents=e,
                        restrictions=restrictions)

class Purify(Action):
    def __init__(self,properties=[],equivalents=[],restrictions=[]):
        name = self.__class__.__name__
        e = equivalents + [ae.NameEquivalentClass(name)]
        p = properties + [pp.MayUseInstrument(default_value=Pipette),
                          pp.MayUseApparatus(default_value=Centrifuge),
                          pp.MayUseApparatus(default_value=Incubator)]
        super().__init__(properties=p,equivalents=e,
                        restrictions=restrictions)

class Bind(Action):
    def __init__(self,properties=[],equivalents=[],restrictions=[]):
        name = self.__class__.__name__
        e = equivalents + [ae.NameEquivalentClass(name)]
        p = properties + [pp.MayUseInstrument(default_value=Pipette),
                          pp.MayUseApparatus(default_value=Centrifuge)]
        super().__init__(properties=p,equivalents=e,
                        restrictions=restrictions)

class Wash(Action):
    def __init__(self,properties=[],equivalents=[],restrictions=[]):
        name = self.__class__.__name__
        e = equivalents + [ae.NameEquivalentClass(name)]
        p = properties + [pp.MayUseInstrument(default_value=Pipette),
                          pp.MayUseApparatus(default_value=Centrifuge)]
        super().__init__(properties=p,equivalents=e,
                        restrictions=restrictions)

class Elution(Action):
    def __init__(self,properties=[],equivalents=[],restrictions=[]):
        name = self.__class__.__name__
        e = equivalents + [ae.NameEquivalentClass(name)]
        p = properties + [pp.MayUseInstrument(default_value=Pipette),
                          pp.MayUseApparatus(default_value=Centrifuge),
                          pp.MayUseApparatus(default_value=Incubator)]
        super().__init__(properties=p,equivalents=e,
                        restrictions=restrictions)


class Transfer(Action):
    def __init__(self,properties=[],equivalents=[],restrictions=[]):
        name = [self.__class__.__name__.lower(),"dispense"]
        e = equivalents + [ae.NameEquivalentClass(name),
                           pe.TransferEquivalent()]
        p = properties + [ap.Source(Well),
                          ap.Destination(Well),
                          ap.Volume(),
                          pp.MayUseInstrument(default_value=Pipette)]
        r = restrictions + [ar.TransferRecipe()]
        super().__init__(properties=p,equivalents=e,
                        restrictions=restrictions)


class Seal(Action):
    def __init__(self,properties=[],equivalents=[],restrictions=[]):
        name = self.__class__.__name__.lower()
        e = equivalents + [ae.NameEquivalentClass(name)]
        p = properties + [ap.Object(Container)]
        super().__init__(properties=p,equivalents=e,
                        restrictions=restrictions)

class Unseal(Action):
    def __init__(self,properties=[],equivalents=[],restrictions=[]):
        name = self.__class__.__name__.lower()
        e = equivalents + [ae.NameEquivalentClass(name)]
        p = properties + [ap.Object(Container)]
        super().__init__(properties=p,equivalents=e,
                        restrictions=restrictions)

class Spin(Action):
    def __init__(self,properties=[],equivalents=[],restrictions=[]):
        name = self.__class__.__name__.lower()
        e = equivalents + [ae.NameEquivalentClass(name)]
        p = properties + [ap.Object(Container),
                          ap.Speed(),
                          ap.Duration(),
                          pp.MayUseApparatus(default_value=Centrifuge)]
        super().__init__(properties=p,equivalents=e,
                        restrictions=restrictions)

class SeperateGel(Action):
    def __init__(self,properties=[],equivalents=[],restrictions=[]):
        name = [self.__class__.__name__.lower(),"gel_separate"]
        e = equivalents + [ae.NameEquivalentClass(name)]
        p = properties + [ap.Source(Well),
                          ap.Duration(),
                          ap.Volume()]
        super().__init__(properties=p,equivalents=e,
                        restrictions=restrictions)

class ColonyPick(Action):
    def __init__(self,properties=[],equivalents=[],restrictions=[]):
        name = [self.__class__.__name__.lower(),"autopick"]
        e = equivalents + [ae.NameEquivalentClass(name)]
        p = properties + [ap.Source(Well),
                          ap.Destination(Well)]
        super().__init__(properties=p,equivalents=e,
                        restrictions=restrictions)
                        
class Incubate(Action):
    def __init__(self,properties=[],equivalents=[],restrictions=[]):
        name = self.__class__.__name__.lower()
        e = equivalents + [ae.NameEquivalentClass(name)]
        p = properties + [ap.Object(Container),
                          ap.Temperature(),
                          ap.Duration(),
                          pp.MayUseApparatus(default_value=Incubator)]
        super().__init__(properties=p,equivalents=e,
                        restrictions=restrictions)

class Thermocycle(Action):
    def __init__(self,properties=[],equivalents=[],restrictions=[]):
        name = self.__class__.__name__.lower()
        e = equivalents + [ae.NameEquivalentClass(name)]
        p = properties + [ap.Object(Container),
                          ap.Cycles(),
                          ap.Temperature(),
                          ap.Duration(),
                          pp.MayUseApparatus(default_value=Thermocycler)]
        super().__init__(properties=p,equivalents=e,
                        restrictions=restrictions)

class Extract(Action): # Source
    def __init__(self,properties=[],equivalents=[],restrictions=[]):
        if equivalents == []:
            e = [pe.ExtractEquivalent()]
        else:
            e = equivalents
        p = properties + [ap.Source(Well)]
        super().__init__(properties=p,equivalents=e,
                        restrictions=restrictions)

class Dispense(Action): # Location
    def __init__(self,properties=[],equivalents=[],restrictions=[]):
        if equivalents == []:
            e = [pe.DispenseEquivalent()]
        else:
            e = equivalents
        p = properties + [ap.Destination(Well)]
        super().__init__(properties=p,equivalents=e,
                        restrictions=restrictions)

class Consolidate(Action):
    def __init__(self,properties=[],equivalents=[],restrictions=[]):
        if equivalents == []:
            e = [pe.ConsolidateEquivalent()]
        else:
            e = equivalents
        super().__init__(properties=properties,equivalents=e,
                        restrictions=restrictions)

class Distribute(Action):
    def __init__(self,properties=[],equivalents=[],restrictions=[]):
        if equivalents == []:
            e = [pe.DistributeEquivalent()]
        else:
            e = equivalents
        super().__init__(properties=properties,equivalents=e,
                        restrictions=restrictions)

