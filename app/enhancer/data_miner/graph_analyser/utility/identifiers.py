import rdflib

class SBOLIdentifiers:
    def __init__(self):
        self.namespaces = Namespace()
        self.objects = Objects(self.namespaces)
        self.predicates = Predicates(self.namespaces)
    
class Namespace:
    def __init__(self):
        self.sbol = rdflib.URIRef('http://sbols.org/v2#')
        identifiers = rdflib.URIRef('http://identifiers.org/')
        self.sequence_ontology = rdflib.URIRef(identifiers + 'so/SO:')
        self.sbo_biomodels = rdflib.URIRef(identifiers + 'biomodels.sbo/SBO:') 
        self.identifier_edam = rdflib.URIRef(identifiers + 'edam/')

        self.biopax = rdflib.URIRef('http://www.biopax.org/release/biopax-level3.owl#')
        self.dc = rdflib.URIRef('http://purl.org/dc/terms/')
        self.edam = rdflib.URIRef('http://edamontology.org/format')
        self.owl = rdflib.URIRef('http://www.w3.org/2002/07/owl#')
        self.prov = rdflib.URIRef('http://www.w3.org/ns/prov#')
        self.synbiohub = rdflib.URIRef('http://wiki.synbiohub.org/wiki/Terms/synbiohub#')

        self.prune = ["http://purl.org/dc/elements/1.1/",
                      "http://purl.obolibrary.org/obo/"]

class Objects:
    def __init__(self, namespaces):
        self.namespaces = namespaces
        self.component_definition = rdflib.term.URIRef(self.namespaces.sbol + 'ComponentDefinition')
        self.component = rdflib.term.URIRef(self.namespaces.sbol + 'Component')
        self.module_definition = rdflib.term.URIRef(self.namespaces.sbol + 'ModuleDefinition')
        self.range = rdflib.term.URIRef(self.namespaces.sbol + 'Range')
        self.cut = rdflib.term.URIRef(self.namespaces.sbol + 'Cut')
        self.sequence = rdflib.term.URIRef(self.namespaces.sbol + "Sequence")
        self.combinatorial_derivation = rdflib.term.URIRef(self.namespaces.sbol + "CombinatorialDerivation")
        self.experiment = rdflib.term.URIRef(self.namespaces.sbol + "Experiment")
        self.experimental_data = rdflib.term.URIRef(self.namespaces.sbol + "ExperimentalData")
        self.functional_component = rdflib.term.URIRef(self.namespaces.sbol + "FunctionalComponent")
        self.implementation = rdflib.term.URIRef(self.namespaces.sbol + "Implementation")
        self.interaction = rdflib.term.URIRef(self.namespaces.sbol + "Interaction")
        self.generic_location = rdflib.term.URIRef(self.namespaces.sbol + "GenericLocation")
        self.mapsTo = rdflib.term.URIRef(self.namespaces.sbol + "MapsTo")
        self.module = rdflib.term.URIRef(self.namespaces.sbol + "Module")
        self.model = rdflib.term.URIRef(self.namespaces.sbol + "Model")
        self.attachment = rdflib.term.URIRef(self.namespaces.sbol + "Attachment")
        self.collection = rdflib.term.URIRef(self.namespaces.sbol + "Collection")
        self.sequence_annotation = rdflib.term.URIRef(self.namespaces.sbol + "SequenceAnnotation")
        self.sequence_constraint = rdflib.term.URIRef(self.namespaces.sbol + "SequenceConstraint")
        self.participation = rdflib.term.URIRef(self.namespaces.sbol + "Participation")
        self.activity = rdflib.term.URIRef(self.namespaces.prov + "Activity")
        self.usage = rdflib.term.URIRef(self.namespaces.prov + "Usage")
        self.association = rdflib.term.URIRef(self.namespaces.prov + "Association")
        self.plan = rdflib.term.URIRef(self.namespaces.prov + "Plan")
        self.agent = rdflib.term.URIRef(self.namespaces.prov + "Agent")
        self.public = rdflib.term.URIRef(self.namespaces.sbol + "public")
        self.inout = rdflib.term.URIRef(self.namespaces.sbol + "inout")
        self.naseq = rdflib.term.URIRef("http://www.chem.qmul.ac.uk/iubmb/misc/naseq.html")
        self.amino_acid = rdflib.term.URIRef("http://www.chem.qmul.ac.uk/iupac/AminoAcid/")
        self.opensmiles = rdflib.term.URIRef("http://www.opensmiles.org/opensmiles.html")
        self.DNA = rdflib.term.URIRef(namespaces.biopax + "Dna")
        self.DNARegion = rdflib.term.URIRef(namespaces.biopax + "DnaRegion")
        self.RNA = rdflib.term.URIRef(namespaces.biopax + "Rna")
        self.RNARegion = rdflib.term.URIRef(namespaces.biopax + "RnaRegion")
        self.protein = rdflib.term.URIRef(namespaces.biopax + "Protein")
        self.smallMolecule = rdflib.term.URIRef(namespaces.biopax + "SmallMolecule")
        self.complex = rdflib.term.URIRef(namespaces.biopax + "Complex")

class Predicates:
    def __init__(self, namespaces):
        self.namespaces = namespaces
        self.rdf_type = rdflib.URIRef(rdflib.RDF.type)

        self.display_id = rdflib.term.URIRef(self.namespaces.sbol + 'displayId')
        self.persistent_identity = rdflib.term.URIRef(self.namespaces.sbol + 'persistentIdentity')
        self.version = rdflib.term.URIRef(self.namespaces.sbol + 'version')
        self.title = rdflib.term.URIRef(self.namespaces.dc + 'title')
        self.description = rdflib.term.URIRef(self.namespaces.dc + 'description')


        self.component = rdflib.term.URIRef(self.namespaces.sbol + 'component')
        self.functional_component = rdflib.term.URIRef(self.namespaces.sbol + 'functionalComponent')
        self.sequence_annotation = rdflib.term.URIRef(self.namespaces.sbol + 'sequenceAnnotation')
        self.sequence_constraint = rdflib.term.URIRef(self.namespaces.sbol + 'sequenceConstraint')
        self.location = rdflib.term.URIRef(self.namespaces.sbol + 'location')
        self.sequence = rdflib.term.URIRef(self.namespaces.sbol + 'sequence')
        self.cut = rdflib.term.URIRef(self.namespaces.sbol + 'cut')
        self.at = rdflib.term.URIRef(self.namespaces.sbol + 'at')

        self.definition = rdflib.term.URIRef(self.namespaces.sbol + 'definition')
        self.sequence_constraint_restriction = rdflib.term.URIRef(self.namespaces.sbol + 'restriction')
        self.sequence_constraint_subject = rdflib.term.URIRef(self.namespaces.sbol + 'subject')
        self.sequence_constraint_object = rdflib.term.URIRef(self.namespaces.sbol + 'object')
        self.type = rdflib.term.URIRef(self.namespaces.sbol + 'type')
        self.role = rdflib.term.URIRef(self.namespaces.sbol + 'role')
        self.start = rdflib.term.URIRef(self.namespaces.sbol + 'start')
        self.end = rdflib.term.URIRef(self.namespaces.sbol + 'end')

        self.interaction = rdflib.term.URIRef(self.namespaces.sbol + 'interaction')
        self.participation = rdflib.term.URIRef(self.namespaces.sbol + 'participation')
        self.elements = rdflib.term.URIRef(self.namespaces.sbol + 'elements')
        self.participant = rdflib.term.URIRef(self.namespaces.sbol + 'participant')
        self.encoding = rdflib.term.URIRef(self.namespaces.sbol + 'encoding')
        self.direction = rdflib.term.URIRef(self.namespaces.sbol + 'direction')
        self.access = rdflib.term.URIRef(self.namespaces.sbol + 'access')
        self.orientation = rdflib.term.URIRef(self.namespaces.sbol + 'orientation')

        self.framework = rdflib.term.URIRef(self.namespaces.sbol + 'framework')
        self.language = rdflib.term.URIRef(self.namespaces.sbol + 'language')
        self.source = rdflib.term.URIRef(self.namespaces.sbol + 'source')

        self.local = rdflib.term.URIRef(self.namespaces.sbol + 'local')
        self.remote = rdflib.term.URIRef(self.namespaces.sbol + 'remote')
        self.module = rdflib.term.URIRef(self.namespaces.sbol + 'module')
        self.maps_to = rdflib.term.URIRef(self.namespaces.sbol + 'mapsTo')
        self.variable_component = rdflib.term.URIRef(self.namespaces.sbol + 'variableComponent')
        self.size = rdflib.term.URIRef(self.namespaces.sbol + 'size')
        self.hash = rdflib.term.URIRef(self.namespaces.sbol + 'hash')
        self.format = rdflib.term.URIRef(self.namespaces.sbol + 'format')
        self.attachment = rdflib.term.URIRef(self.namespaces.sbol + 'attachment')
        self.member = rdflib.term.URIRef(self.namespaces.sbol + 'member')
        self.refinement = rdflib.term.URIRef(self.namespaces.sbol + "refinement")
        self.model = rdflib.term.URIRef(self.namespaces.sbol + "model")

        self.mutable_notes = rdflib.term.URIRef(self.namespaces.synbiohub + 'mutableNotes')
        self.mutable_description = rdflib.term.URIRef(self.namespaces.synbiohub + 'mutableDescription')
        self.mutable_provenance = rdflib.term.URIRef(self.namespaces.synbiohub + 'mutableProvenance')
        self.toplevel = rdflib.term.URIRef(self.namespaces.synbiohub + 'topLevel')
        self.ownedby = rdflib.term.URIRef(self.namespaces.synbiohub + 'ownedBy')

        self.created = rdflib.term.URIRef(self.namespaces.dc + 'created')

        self.was_generated_by = rdflib.term.URIRef(self.namespaces.prov + 'wasGeneratedBy') 
        self.ended_at_time = rdflib.term.URIRef(self.namespaces.prov + 'endedAtTime')
        self.had_plan = rdflib.term.URIRef(self.namespaces.prov + 'hadPlan')
        self.entity = rdflib.term.URIRef(self.namespaces.prov + 'entity')
        self.qualified_association = rdflib.term.URIRef(self.namespaces.prov + 'qualifiedAssociation')
        self.qualified_usage = rdflib.term.URIRef(self.namespaces.prov + 'qualifiedUsage')
        self.agent = rdflib.term.URIRef(self.namespaces.prov + 'agent')

        self.ownership_predicates = [
            self.module,
            self.maps_to,
            self.interaction,
            self.participation,
            self.functional_component,
            self.sequence_constraint,
            self.location,
            self.sequence_annotation,
            self.variable_component
        ] 
        
        self.prune = [
            self.display_id,
            self.version,
            self.persistent_identity
        ]

identifiers = SBOLIdentifiers()