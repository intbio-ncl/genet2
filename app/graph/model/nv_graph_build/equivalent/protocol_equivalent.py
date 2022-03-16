from equivalent.abstract_equivalent import ConceptualEquivalent
from equivalent.abstract_equivalent import PhysicalEquivalent
from restriction import protocol_restriction as pr

class ActionEquivalent(ConceptualEquivalent):
    def __init__(self):
        restrictions = [pr.ActionRestriction()]
        super().__init__(restrictions)

class ContainerEquivalent(PhysicalEquivalent):
    def __init__(self):
        restrictions = [pr.ContainerRestriction()]
        super().__init__(restrictions)

class InstrumentEquivalent(PhysicalEquivalent):
    def __init__(self):
        restrictions = [pr.InstrumentRestriction()]
        super().__init__(restrictions)

class PipetteEquivalent(PhysicalEquivalent):
    def __init__(self):
        restrictions = [pr.PipetteRestriction()]
        super().__init__(restrictions)

class ProtocolEquivalent(PhysicalEquivalent):
    def __init__(self):
        restrictions = [pr.ProtocolRestriction()]
        super().__init__(restrictions)

class ApparatusEquivalent(PhysicalEquivalent):
    def __init__(self):
        restrictions = [pr.ApparatusRestriction()]
        super().__init__(restrictions)

class WellEquivalent(PhysicalEquivalent):
    def __init__(self):
        restrictions = [pr.WellRestriction()]
        super().__init__(restrictions)

class ExtractEquivalent(ConceptualEquivalent):
    def __init__(self):
        restrictions = [pr.OneSourceRestriction(),
                        pr.ZeroDestinationRestriction()]
        super().__init__(restrictions)

class DispenseEquivalent(ConceptualEquivalent):
    def __init__(self):
        restrictions = [pr.ZeroSourceRestriction(),
                        pr.OneDestinationRestriction()]
        super().__init__(restrictions)

class TransferEquivalent(ConceptualEquivalent):
    def __init__(self):
        restrictions = [pr.OneSourceRestriction(),
                        pr.OneDestinationRestriction()]
        super().__init__(restrictions)

class ConsolidateEquivalent(ConceptualEquivalent):
    def __init__(self):
        restrictions = [pr.ManySourceRestriction(),
                        pr.OneDestinationRestriction()]
        super().__init__(restrictions)

class DistributeEquivalent(ConceptualEquivalent):
    def __init__(self):
        restrictions = [pr.OneSourceRestriction(),
                        pr.ManyDestinationRestriction()]
        super().__init__(restrictions)