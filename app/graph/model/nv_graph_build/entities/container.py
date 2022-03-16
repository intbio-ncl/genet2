from entities.abstract_entity import PhysicalEntity
from property import protocols as prot
from equivalent import protocol_equivalent as pe
from equivalent import abstract_equivalent as ab

class Well(PhysicalEntity):
    def __init__(self,properties=[],equivalents=[],restrictions=[]):
        if equivalents == []:
            e = [pe.WellEquivalent()]
        else:
            e = equivalents
        super().__init__(properties=properties,equivalents=e,restrictions=restrictions)

class Container(PhysicalEntity):
    def __init__(self,properties=[],equivalents=[],restrictions=[]):
        if equivalents == []:
            e = [pe.ContainerEquivalent()]
        else:
            e = equivalents
        super().__init__(properties=properties,equivalents=e,restrictions=restrictions)

class Flat384(Container):
    def __init__(self,properties=[],equivalents=[],restrictions=[]):
        name = "384-flat"
        e = equivalents + [ab.NameEquivalentClass(name)]
        p = properties + [prot.ColNum(default_value=24),
                          prot.RowNum(default_value=16),
                          prot.Well(Well)]
        super().__init__(properties=p,equivalents=e,
                        restrictions=restrictions)

class PCR384(Container):
    def __init__(self,properties=[],equivalents=[],restrictions=[]):
        name = "384-pcr"
        e = equivalents + [ab.NameEquivalentClass(name)]
        p = properties + [prot.ColNum(default_value=24),
                          prot.RowNum(default_value=16),
                          prot.Well(Well)]
        super().__init__(properties=p,equivalents=e,
                        restrictions=restrictions)

class Echo384(Container):
    def __init__(self,properties=[],equivalents=[],restrictions=[]):
        name = "384-echo"
        e = equivalents + [ab.NameEquivalentClass(name)]
        p = properties + [prot.ColNum(default_value=24),
                          prot.RowNum(default_value=16),
                          prot.Well(Well)]
        super().__init__(properties=p,equivalents=e,
                        restrictions=restrictions)

class Flat96(Container):
    def __init__(self,properties=[],equivalents=[],restrictions=[]):
        name = "96-flat"
        e = equivalents + [ab.NameEquivalentClass(name)]
        p = properties + [prot.ColNum(default_value=12),
                          prot.RowNum(default_value=8),
                          prot.Well(Well)]
        super().__init__(properties=p,equivalents=e,
                        restrictions=restrictions)

class PCR96(Container):
    def __init__(self,properties=[],equivalents=[],restrictions=[]):
        name = "96-pcr"
        e = equivalents + [ab.NameEquivalentClass(name)]
        p = properties + [prot.ColNum(default_value=12),
                          prot.RowNum(default_value=8),
                          prot.Well(Well)]
        super().__init__(properties=p,equivalents=e,
                        restrictions=restrictions)

class Echo96(Container):
    def __init__(self,properties=[],equivalents=[],restrictions=[]):
        name = "96-echo"
        e = equivalents + [ab.NameEquivalentClass(name)]
        p = properties + [prot.ColNum(default_value=12),
                          prot.RowNum(default_value=8),
                          prot.Well(Well)]
        super().__init__(properties=p,equivalents=e,
                        restrictions=restrictions)

class Deep96(Container):
    def __init__(self,properties=[],equivalents=[],restrictions=[]):
        name = "96-deep"
        e = equivalents + [ab.NameEquivalentClass(name)]
        p = properties + [prot.ColNum(default_value=12),
                          prot.RowNum(default_value=8),
                          prot.Well(Well)]
        super().__init__(properties=p,equivalents=e,
                        restrictions=restrictions)

class Deep24(Container):
    def __init__(self,properties=[],equivalents=[],restrictions=[]):
        name = "24-deep"
        e = equivalents + [ab.NameEquivalentClass(name)]
        p = properties + [prot.ColNum(default_value=6),
                          prot.RowNum(default_value=4),
                          prot.Well(Well)]
        super().__init__(properties=p,equivalents=e,
                        restrictions=restrictions)

class Micro2(Container):
    def __init__(self,properties=[],equivalents=[],restrictions=[]):
        name = "micro-2.0"
        e = equivalents + [ab.NameEquivalentClass(name)]
        p = properties + [prot.ColNum(default_value=1),
                          prot.RowNum(default_value=1),
                          prot.Well(Well)]
        super().__init__(properties=p,equivalents=e,
                        restrictions=restrictions)

class Micro15(Container):
    def __init__(self,properties=[],equivalents=[],restrictions=[]):
        name = "micro-1.5"
        e = equivalents + [ab.NameEquivalentClass(name)]
        p = properties + [prot.ColNum(default_value=1),
                          prot.RowNum(default_value=1),
                          prot.Well(Well)]
        super().__init__(properties=p,equivalents=e,
                        restrictions=restrictions)

class Flat6(Container):
    def __init__(self,properties=[],equivalents=[],restrictions=[]):
        name = "6-flat"
        e = equivalents + [ab.NameEquivalentClass(name)]
        p = properties + [prot.ColNum(default_value=3),
                          prot.RowNum(default_value=2),
                          prot.Well(Well)]
        super().__init__(properties=p,equivalents=e,
                        restrictions=restrictions)

class Flat1(Container):
    def __init__(self,properties=[],equivalents=[],restrictions=[]):
        name = "1-flat"
        e = equivalents + [ab.NameEquivalentClass(name)]
        p = properties + [prot.ColNum(default_value=1),
                          prot.RowNum(default_value=1),
                          prot.Well(Well)]
        super().__init__(properties=p,equivalents=e,
                        restrictions=restrictions)

class Reservoir8(Container):
    def __init__(self,properties=[],equivalents=[],restrictions=[]):
        name = "res-mw8-hp"
        e = equivalents + [ab.NameEquivalentClass(name)]
        p = properties + [prot.ColNum(default_value=1),
                          prot.RowNum(default_value=8),
                          prot.Well(Well)]
        super().__init__(properties=p,equivalents=e,
                        restrictions=restrictions)

class Reservoir12(Container):
    def __init__(self,properties=[],equivalents=[],restrictions=[]):
        name = "res-mw12-hp"
        e = equivalents + [ab.NameEquivalentClass(name)]
        p = properties + [prot.ColNum(default_value=1),
                          prot.RowNum(default_value=12),
                          prot.Well(Well)]
        super().__init__(properties=p,equivalents=e,
                        restrictions=restrictions)

def _gen_names(obj,c_name):
    return [obj.__class__.__name__,
            obj.__class__.__name__.lower(),
            obj.__class__.__name__.upper(),
            c_name]