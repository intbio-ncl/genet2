import rdflib
from rdflib import URIRef
class SBOLIdentifiers:
    def __init__(self):
        self.namespaces = Namespace()
        self.objects = Objects(self.namespaces)
        self.predicates = Predicates(self.namespaces)
        self.roles = Roles(self.namespaces)
    
class Namespace:
    def __init__(self):
        self.sbol = URIRef('http://sbols.org/v2#')
        identifiers = URIRef('http://identifiers.org/')
        self.sequence_ontology = URIRef(identifiers + 'so/SO:')
        self.sbo_biomodels = URIRef(identifiers + 'biomodels.sbo/SBO:') 
        self.identifier_edam = URIRef(identifiers + 'edam/')

        self.biopax = URIRef('http://www.biopax.org/release/biopax-level3.owl#')
        self.dc = URIRef('http://purl.org/dc/terms/')
        self.edam = URIRef('http://edamontology.org/format')
        self.owl = URIRef('http://www.w3.org/2002/07/owl#')
        self.prov = URIRef('http://www.w3.org/ns/prov#')
        self.synbiohub = URIRef('http://wiki.synbiohub.org/wiki/Terms/synbiohub#')
        self.igem = URIRef("http://wiki.synbiohub.org/wiki/Terms/igem#")
        self.prune = ["http://purl.org/dc/elements/1.1/",
                      "http://purl.obolibrary.org/obo/"]

class Objects:
    def __init__(self, namespaces):
        self.namespaces = namespaces
        self.component_definition = URIRef(self.namespaces.sbol + 'ComponentDefinition')
        self.component = URIRef(self.namespaces.sbol + 'Component')
        self.module_definition = URIRef(self.namespaces.sbol + 'ModuleDefinition')
        self.range = URIRef(self.namespaces.sbol + 'Range')
        self.cut = URIRef(self.namespaces.sbol + 'Cut')
        self.sequence = URIRef(self.namespaces.sbol + "Sequence")
        self.combinatorial_derivation = URIRef(self.namespaces.sbol + "CombinatorialDerivation")
        self.experiment = URIRef(self.namespaces.sbol + "Experiment")
        self.experimental_data = URIRef(self.namespaces.sbol + "ExperimentalData")
        self.functional_component = URIRef(self.namespaces.sbol + "FunctionalComponent")
        self.implementation = URIRef(self.namespaces.sbol + "Implementation")
        self.interaction = URIRef(self.namespaces.sbol + "Interaction")
        self.generic_location = URIRef(self.namespaces.sbol + "GenericLocation")
        self.mapsTo = URIRef(self.namespaces.sbol + "MapsTo")
        self.module = URIRef(self.namespaces.sbol + "Module")
        self.model = URIRef(self.namespaces.sbol + "Model")
        self.attachment = URIRef(self.namespaces.sbol + "Attachment")
        self.collection = URIRef(self.namespaces.sbol + "Collection")
        self.sequence_annotation = URIRef(self.namespaces.sbol + "SequenceAnnotation")
        self.sequence_constraint = URIRef(self.namespaces.sbol + "SequenceConstraint")
        self.participation = URIRef(self.namespaces.sbol + "Participation")
        self.activity = URIRef(self.namespaces.prov + "Activity")
        self.usage = URIRef(self.namespaces.prov + "Usage")
        self.association = URIRef(self.namespaces.prov + "Association")
        self.plan = URIRef(self.namespaces.prov + "Plan")
        self.agent = URIRef(self.namespaces.prov + "Agent")
        self.public = URIRef(self.namespaces.sbol + "public")
        self.inout = URIRef(self.namespaces.sbol + "inout")
        self.naseq = URIRef("http://www.chem.qmul.ac.uk/iubmb/misc/naseq.html")
        self.amino_acid = URIRef("http://www.chem.qmul.ac.uk/iupac/AminoAcid/")
        self.opensmiles = URIRef("http://www.opensmiles.org/opensmiles.html")
        self.DNA = URIRef(namespaces.biopax + "Dna")
        self.DNARegion = URIRef(namespaces.biopax + "DnaRegion")
        self.RNA = URIRef(namespaces.biopax + "Rna")
        self.RNARegion = URIRef(namespaces.biopax + "RnaRegion")
        self.protein = URIRef(namespaces.biopax + "Protein")
        self.smallMolecule = URIRef(namespaces.biopax + "SmallMolecule")
        self.complex = URIRef(namespaces.biopax + "Complex")

class Predicates:
    def __init__(self, namespaces):
        self.namespaces = namespaces
        self.rdf_type = URIRef(rdflib.RDF.type)

        self.display_id = URIRef(self.namespaces.sbol + 'displayId')
        self.persistent_identity = URIRef(self.namespaces.sbol + 'persistentIdentity')
        self.version = URIRef(self.namespaces.sbol + 'version')
        self.title = URIRef(self.namespaces.dc + 'title')
        self.description = URIRef(self.namespaces.dc + 'description')


        self.component = URIRef(self.namespaces.sbol + 'component')
        self.functional_component = URIRef(self.namespaces.sbol + 'functionalComponent')
        self.sequence_annotation = URIRef(self.namespaces.sbol + 'sequenceAnnotation')
        self.sequence_constraint = URIRef(self.namespaces.sbol + 'sequenceConstraint')
        self.location = URIRef(self.namespaces.sbol + 'location')
        self.sequence = URIRef(self.namespaces.sbol + 'sequence')
        self.cut = URIRef(self.namespaces.sbol + 'cut')
        self.at = URIRef(self.namespaces.sbol + 'at')

        self.definition = URIRef(self.namespaces.sbol + 'definition')
        self.sequence_constraint_restriction = URIRef(self.namespaces.sbol + 'restriction')
        self.sequence_constraint_subject = URIRef(self.namespaces.sbol + 'subject')
        self.sequence_constraint_object = URIRef(self.namespaces.sbol + 'object')
        self.type = URIRef(self.namespaces.sbol + 'type')
        self.role = URIRef(self.namespaces.sbol + 'role')
        self.start = URIRef(self.namespaces.sbol + 'start')
        self.end = URIRef(self.namespaces.sbol + 'end')

        self.interaction = URIRef(self.namespaces.sbol + 'interaction')
        self.participation = URIRef(self.namespaces.sbol + 'participation')
        self.elements = URIRef(self.namespaces.sbol + 'elements')
        self.participant = URIRef(self.namespaces.sbol + 'participant')
        self.encoding = URIRef(self.namespaces.sbol + 'encoding')
        self.direction = URIRef(self.namespaces.sbol + 'direction')
        self.access = URIRef(self.namespaces.sbol + 'access')
        self.orientation = URIRef(self.namespaces.sbol + 'orientation')

        self.framework = URIRef(self.namespaces.sbol + 'framework')
        self.language = URIRef(self.namespaces.sbol + 'language')
        self.source = URIRef(self.namespaces.sbol + 'source')

        self.local = URIRef(self.namespaces.sbol + 'local')
        self.remote = URIRef(self.namespaces.sbol + 'remote')
        self.module = URIRef(self.namespaces.sbol + 'module')
        self.maps_to = URIRef(self.namespaces.sbol + 'mapsTo')
        self.variable_component = URIRef(self.namespaces.sbol + 'variableComponent')
        self.size = URIRef(self.namespaces.sbol + 'size')
        self.hash = URIRef(self.namespaces.sbol + 'hash')
        self.format = URIRef(self.namespaces.sbol + 'format')
        self.attachment = URIRef(self.namespaces.sbol + 'attachment')
        self.member = URIRef(self.namespaces.sbol + 'member')
        self.refinement = URIRef(self.namespaces.sbol + "refinement")
        self.model = URIRef(self.namespaces.sbol + "model")

        self.mutable_notes = URIRef(self.namespaces.synbiohub + 'mutableNotes')
        self.mutable_description = URIRef(self.namespaces.synbiohub + 'mutableDescription')
        self.mutable_provenance = URIRef(self.namespaces.synbiohub + 'mutableProvenance')
        self.toplevel = URIRef(self.namespaces.synbiohub + 'topLevel')
        self.ownedby = URIRef(self.namespaces.synbiohub + 'ownedBy')

        self.created = URIRef(self.namespaces.dc + 'created')

        self.was_generated_by = URIRef(self.namespaces.prov + 'wasGeneratedBy') 
        self.ended_at_time = URIRef(self.namespaces.prov + 'endedAtTime')
        self.had_plan = URIRef(self.namespaces.prov + 'hadPlan')
        self.entity = URIRef(self.namespaces.prov + 'entity')
        self.qualified_association = URIRef(self.namespaces.prov + 'qualifiedAssociation')
        self.qualified_usage = URIRef(self.namespaces.prov + 'qualifiedUsage')
        self.agent = URIRef(self.namespaces.prov + 'agent')

        self.prune = [
            self.display_id,
            self.version,
            self.persistent_identity
        ]

class Roles:
    def __init__(self, namespaces):
        namespaces = namespaces
        self.DNA = URIRef(namespaces.biopax + "Dna")
        self.DNARegion = URIRef(namespaces.biopax + "DnaRegion")
        self.RNA = URIRef(namespaces.biopax + "Rna")
        self.RNARegion = URIRef(namespaces.biopax + "RnaRegion")
        self.protein = URIRef(namespaces.biopax + "Protein")
        self.smallMolecule = URIRef(namespaces.biopax + "SmallMolecule")
        self.complex = URIRef(namespaces.biopax + "Complex")

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

        self.inline = URIRef(namespaces.sbol + "inline")
        self.reverse = URIRef(namespaces.sbol + "reverseComplement")

        self.igem_promoter = URIRef(namespaces.igem + 'feature/promoter')
        self.igem_rbs = URIRef(namespaces.igem + 'feature/rbs')
        self.igem_cds = URIRef(namespaces.igem + 'feature/cds')
        self.igem_terminator = URIRef(namespaces.igem + 'feature/terminator')
        self.igem_protein = URIRef(namespaces.igem + 'feature/protein')

identifiers = SBOLIdentifiers()