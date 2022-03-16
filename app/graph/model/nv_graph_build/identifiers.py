from os import name
from rdflib import URIRef,RDF

class Identifiers:
    def __init__(self):
        self.namespaces = Namespace()
        self.predicates = Predicates(self.namespaces)
        self.roles = Roles(self.namespaces)
    
class Namespace:
    def __init__(self):
        identifiers = URIRef('http://identifiers.org/')
        self.nv = URIRef("http://www.nv_ontology.org/")
        self.sequence_ontology = URIRef(identifiers + 'so/SO:')
        self.sbo_biomodels = URIRef(identifiers + 'biomodels.sbo/SBO:') 
        self.identifier_edam = URIRef(identifiers + 'edam/')
        self.biopax = URIRef('http://www.biopax.org/release/biopax-level3.owl#')
        self.dc = URIRef('http://purl.org/dc/terms/')
        self.edam = URIRef('http://edamontology.org/')
        self.edam_format = URIRef(self.edam + "format")
        self.prov = URIRef('http://www.w3.org/ns/prov#')
        self.efo = URIRef("http://www.ebi.ac.uk/efo/EFO")
        self.obi = URIRef("http://purl.obolibrary.org/obo/OBI")

class Predicates:
    def __init__(self, namespaces):
        namespaces = namespaces
        self.rdf_type = URIRef(RDF.type)

class Roles:
    def __init__(self, namespaces):
        namespaces = namespaces

        self.physical_entity = URIRef(namespaces.biopax + "PhysicalEntity")
        self.conceptual_entity = URIRef(namespaces.biopax + "Interaction") # This tag isn't great.

        self.DNA = URIRef(namespaces.biopax + "Dna")
        self.DNARegion = URIRef(namespaces.biopax + "DnaRegion")
        self.RNA = URIRef(namespaces.biopax + "Rna")
        self.RNARegion = URIRef(namespaces.biopax + "RnaRegion")
        self.protein = URIRef(namespaces.biopax + "Protein")
        self.smallMolecule = URIRef(namespaces.biopax + "SmallMolecule")
        self.complex = URIRef(namespaces.biopax + "Complex")
        self.all = URIRef("www.placeholder.com/all_type")

        self.promoter       = URIRef(namespaces.sequence_ontology + "0000167")
        self.rbs            = URIRef(namespaces.sequence_ontology + "0000139")
        self.cds            = URIRef(namespaces.sequence_ontology + "0000316")
        self.terminator     = URIRef(namespaces.sequence_ontology + "0000141")
        self.gene           = URIRef(namespaces.sequence_ontology + "0000704")
        self.operator       = URIRef(namespaces.sequence_ontology + "0000057")
        self.engineeredGene = URIRef(namespaces.sequence_ontology + "0000280")
        self.mRNA           = URIRef(namespaces.sequence_ontology + "0000234")
        self.engineeredRegion = URIRef(namespaces.sequence_ontology + "0000804")
        self.nonCovBindingSite = URIRef(namespaces.sequence_ontology + "0001091")
        self.effector       = URIRef("http://identifiers.org/chebi/CHEBI:35224") 
        self.startCodon     = URIRef(namespaces.sequence_ontology + "0000318")
        self.tag            = URIRef(namespaces.sequence_ontology + "0000324")
        self.engineeredTag  = URIRef(namespaces.sequence_ontology + "0000807")
        self.sgRNA          = URIRef(namespaces.sequence_ontology + "0001998")
        self.transcriptionFactor = URIRef("http://identifiers.org/go/GO:0003700")

        self.inhibition = URIRef(namespaces.sbo_biomodels + "0000169")
        self.stimulation = URIRef(namespaces.sbo_biomodels + "0000170")
        self.biochemical_reaction = URIRef(namespaces.sbo_biomodels + "0000176")
        self.noncovalent_bonding = URIRef(namespaces.sbo_biomodels + "0000177")
        self.association = URIRef(namespaces.biopax + "ComplexAssembly")
        self.degradation = URIRef(namespaces.sbo_biomodels + "0000179")
        self.genetic_production = URIRef(namespaces.sbo_biomodels + "0000589")
        self.control = URIRef(namespaces.sbo_biomodels + "0000168")

        self.inhibitor = URIRef(namespaces.sbo_biomodels + "0000020")
        self.inhibited = URIRef(namespaces.sbo_biomodels + "0000642")
        self.stimulator =  URIRef(namespaces.sbo_biomodels + "0000459")
        self.stimulated = URIRef(namespaces.sbo_biomodels + "0000643")
        self.modifier = URIRef(namespaces.sbo_biomodels + "0000019")
        self.modified = URIRef(namespaces.sbo_biomodels + "0000644")
        self.product = URIRef(namespaces.sbo_biomodels + "0000011")
        self.reactant = URIRef(namespaces.sbo_biomodels + "0000010")
        self.gp_promoter = URIRef(namespaces.sbo_biomodels + "0000598") 
        self.template = URIRef(namespaces.sbo_biomodels + "0000645")

        self.translation = URIRef(namespaces.sbo_biomodels + "0000184")
        self.transcription = URIRef(namespaces.sbo_biomodels + "0000183")
        self.dissociation = URIRef(namespaces.sbo_biomodels + "0000180")
        self.hydrolysis = URIRef(namespaces.sbo_biomodels + "0000376")

        self.action = URIRef(namespaces.nv + "Action")
        self.protocol = URIRef(namespaces.edam + "data_2531")
        self.instrument = URIRef(namespaces.efo + "0000548")
        self.pipette = URIRef(namespaces.obi + "0002488")
        self.container = URIRef(namespaces.obi + "0000967")
        self.extract = URIRef(namespaces.obi + "0302884")
        self.well = URIRef(namespaces.nv + "Well")
        self.dispense = URIRef(namespaces.nv + "Dispense")
        self.transfer = URIRef(namespaces.nv + "Transfer")
        self.consolidate = URIRef(namespaces.nv + "Consolidate")
        self.distribute = URIRef(namespaces.nv + "Distribute")
        self.pick = URIRef(namespaces.nv + "Pick")
        self.drop = URIRef(namespaces.nv + "Drop")
        self.external_machine = URIRef(namespaces.nv + "ExternalMachine")

identifiers = Identifiers()