import rdflib

class SBOLIdentifiers:
    def __init__(self):
        self.namespaces = Namespace()
        self.objects = Objects(self.namespaces)
        self.predicates = Predicates(self.namespaces)
        self.external = ExternalIdentifiers(self.namespaces)

    def translate_role(self,role):
        translators = [
            self.external.cd_role_name,
            self.external.cd_type_names,
            self.external.interaction_type_names,
            self.external.inhibition_participants]

        for translator in translators:
            try:
                return translator[role]
            except KeyError:
                continue
        return None
    
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

        self.top_levels = {rdflib.URIRef(self.namespaces.sbol + name) for name in
                            ['Sequence',
                            'ComponentDefinition',
                            'ModuleDefinition',
                            'Model',
                            'Collection',
                            'GenericTopLevel',
                            'Attachment',
                            'Activity',
                            'Agent',
                            'Plan',
                            'Implementation',
                            'CombinatorialDerivation',
                            'Experiment',
                            'ExperimentalData']}

        self.prune = [
            self.agent,
            self.plan,
            self.association,
            self.usage,
            self.activity,
            self.attachment,
            self.implementation,
            self.experimental_data,
            self.experiment,
            self.sequence]

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
            #self.definition,
            self.description,
            self.title,
            self.rdf_type,
            self.start,
            self.end,
            self.at,
            self.type,
            self.role,
            self.member,
            self.sequence_constraint_restriction,
            self.variable_component,
            self.access,
            self.elements,
            self.size,
            self.language,
            self.persistent_identity,
            self.display_id,
            self.version,
            self.encoding,
            self.direction,
            self.orientation,
            self.framework,
            self.source,
            self.toplevel,
            self.ownedby,
            self.was_generated_by,
            self.created,
            self.ended_at_time,
            self.had_plan,
            self.entity,
            self.qualified_association,
            self.qualified_usage,
            self.hash,
            self.format,
            self.attachment,
            self.agent,
            self.sequence,
            self.location,
            self.model,
            self.refinement]

class ExternalIdentifiers:
    def __init__(self, namespaces):
        self.namespaces = namespaces

        self.component_definition_DNA = rdflib.URIRef(self.namespaces.biopax + "Dna")
        self.component_definition_DNARegion = rdflib.URIRef(self.namespaces.biopax + "DnaRegion")
        self.component_definition_RNA = rdflib.URIRef(self.namespaces.biopax + "Rna")
        self.component_definition_RNARegion = rdflib.URIRef(self.namespaces.biopax + "RnaRegion")
        self.component_definition_protein = rdflib.URIRef(self.namespaces.biopax + "Protein")
        self.component_definition_smallMolecule = rdflib.URIRef(self.namespaces.biopax + "SmallMolecule")
        self.component_definition_complex = rdflib.URIRef(self.namespaces.biopax + "Complex")
        self.component_definition_all = rdflib.URIRef("www.placeholder.com/all_type")

        self.component_definition_promoter       = rdflib.URIRef(self.namespaces.sequence_ontology + "0000167")
        self.component_definition_rbs            = rdflib.URIRef(self.namespaces.sequence_ontology + "0000139")
        self.component_definition_cds            = rdflib.URIRef(self.namespaces.sequence_ontology + "0000316")
        self.component_definition_terminator     = rdflib.URIRef(self.namespaces.sequence_ontology + "0000141")
        self.component_definition_gene           = rdflib.URIRef(self.namespaces.sequence_ontology + "0000704")
        self.component_definition_operator       = rdflib.URIRef(self.namespaces.sequence_ontology + "0000057")
        self.component_definition_engineeredGene = rdflib.URIRef(self.namespaces.sequence_ontology + "0000280")
        self.component_definition_mRNA           = rdflib.URIRef(self.namespaces.sequence_ontology + "0000234")
        self.component_definition_engineeredRegion = rdflib.URIRef(self.namespaces.sequence_ontology + "0000804")
        self.component_definition_nonCovBindingSite = rdflib.URIRef(self.namespaces.sequence_ontology + "0001091")
        self.component_definition_effector       = rdflib.URIRef("http://identifiers.org/chebi/CHEBI:35224") 
        self.component_definition_startCodon     = rdflib.URIRef(self.namespaces.sequence_ontology + "0000318")
        self.component_definition_tag            = rdflib.URIRef(self.namespaces.sequence_ontology + "0000324")
        self.component_definition_engineeredTag  = rdflib.URIRef(self.namespaces.sequence_ontology + "0000807")
        self.component_definition_sgRNA          = rdflib.URIRef(self.namespaces.sequence_ontology + "0001998")
        self.component_definition_transcriptionFactor = rdflib.URIRef("http://identifiers.org/go/GO:0003700")

        self.interaction_inhibition = rdflib.URIRef(self.namespaces.sbo_biomodels + "0000169")
        self.interaction_stimulation = rdflib.URIRef(self.namespaces.sbo_biomodels + "0000170")
        self.interaction_biochemical_reaction = rdflib.URIRef(self.namespaces.sbo_biomodels + "0000176")
        self.interaction_noncovalent_bonding = rdflib.URIRef(self.namespaces.sbo_biomodels + "0000177")
        self.interaction_degradation = rdflib.URIRef(self.namespaces.sbo_biomodels + "0000179")
        self.interaction_genetic_production = rdflib.URIRef(self.namespaces.sbo_biomodels + "0000589")
        self.interaction_control = rdflib.URIRef(self.namespaces.sbo_biomodels + "0000168")

        self.participant_inhibitor = rdflib.URIRef(self.namespaces.sbo_biomodels + "0000020")
        self.participant_inhibited = rdflib.URIRef(self.namespaces.sbo_biomodels + "0000642")
        self.participant_stimulator =  rdflib.URIRef(self.namespaces.sbo_biomodels + "0000459")
        self.participant_stimulated = rdflib.URIRef(self.namespaces.sbo_biomodels + "0000643")
        self.participant_modifier = rdflib.URIRef(self.namespaces.sbo_biomodels + "0000019")
        self.participant_modified = rdflib.URIRef(self.namespaces.sbo_biomodels + "0000644")
        self.participant_product = rdflib.URIRef(self.namespaces.sbo_biomodels + "0000011")
        self.participant_reactant = rdflib.URIRef(self.namespaces.sbo_biomodels + "0000010")
        self.participant_participation_promoter = rdflib.URIRef(self.namespaces.sbo_biomodels + "0000598") 
        self.participant_template = rdflib.URIRef(self.namespaces.sbo_biomodels + "0000645")

        self.location_orientation_inline = rdflib.URIRef(self.namespaces.sbol + "inline")
        self.location_orientation_reverseComplement = rdflib.URIRef(self.namespaces.sbol + "reverseComplement")

        self.functional_component_direction_in = rdflib.URIRef(self.namespaces.sbol + "in")
        self.functional_component_direction_out = rdflib.URIRef(self.namespaces.sbol + "out")
        self.functional_component_direction_inout = rdflib.URIRef(self.namespaces.sbol + "inout") 
        self.functional_component_direction_none = rdflib.URIRef(self.namespaces.sbol + "none")

        self.component_instance_acess_public = rdflib.URIRef(self.namespaces.sbol + "public")
        self.component_instance_acess_private = rdflib.URIRef(self.namespaces.sbol + "private")

        self.sequence_encoding_iupacDNA = rdflib.URIRef("http://www.chem.qmul.ac.uk/iubmb/misc/naseq.html")
        self.sequence_encoding_iupacRNA = rdflib.URIRef("http://www.chem.qmul.ac.uk/iubmb/misc/naseq.html")
        self.sequence_encoding_iupacProtein = rdflib.URIRef("http://www.chem.qmul.ac.uk/iupac/AminoAcid/")
        self.sequence_encoding_opensmilesSMILES = rdflib.URIRef("http://www.opensmiles.org/opensmiles.html")

        self.sequence_constraint_restriction_precedes = rdflib.URIRef(self.namespaces.sbol + "precedes")
        self.sequence_constraint_restriction_sameOrientationAs = rdflib.URIRef(self.namespaces.sbol + "sameOrientationAs")
        self.sequence_constraint_restriction_oppositeOrientationAs = rdflib.URIRef(self.namespaces.sbol + "oppositeOrientationAs")
        self.sequence_constraint_restriction_differentFrom = rdflib.URIRef(self.namespaces.sbol + "differentFrom")

        self.model_language_SBML = rdflib.URIRef(self.namespaces.identifier_edam + "format_2585")
        self.model_language_CellML = rdflib.URIRef(self.namespaces.identifier_edam + "format_3240")
        self.model_language_BioPAX = rdflib.URIRef(self.namespaces.identifier_edam + "format_3156")

        self.model_framework_continuous =  rdflib.URIRef(self.namespaces.sbo_biomodels + "0000062")
        self.model_framework_discrete = rdflib.URIRef(self.namespaces.sbo_biomodels + "0000063")

        self.mapsTo_refinement_useRemote = rdflib.URIRef(self.namespaces.sbol + "useRemote")
        self.mapsTo_refinement_useLocal = rdflib.URIRef(self.namespaces.sbol + "useLocal") 
        self.mapsTo_refinement_verifyIdentical  = rdflib.URIRef(self.namespaces.sbol + "verifyIdentical")
        self.mapsTo_refinement_merge = rdflib.URIRef(self.namespaces.sbol + "merge") 

        self.variable_component_cardinality_zeroOrOne = rdflib.URIRef(self.namespaces.sbol + "zeroOrOne") 
        self.variable_component_cardinality_one = rdflib.URIRef(self.namespaces.sbol + "one")
        self.variable_component_cardinality_zeroOrMore = rdflib.URIRef(self.namespaces.sbol + "zeroOrMore")
        self.variable_component_cardinality_oneOrMore = rdflib.URIRef(self.namespaces.sbol + "oneOrMore")


        self.cd_type_names = {
            self.component_definition_DNA : "DNA",
            self.component_definition_DNARegion : "DNA",
            self.component_definition_RNA : "RNA",
            self.component_definition_RNARegion : "RNA",
            self.component_definition_protein : "Protein",
            self.component_definition_smallMolecule : "Small Molecule",
            self.component_definition_complex: "Complex"}



        self.cd_role_name = {self.component_definition_promoter : "Promoter",
                        self.component_definition_rbs : "RBS",
                        self.component_definition_cds : "CDS",
                        self.component_definition_terminator : "Terminator",
                        self.component_definition_engineeredRegion : "Engineered Region",
                        self.component_definition_engineeredGene : "Engineered Gene",
                        self.component_definition_operator : "Operator",
                        self.component_definition_gene : "Gene",
                        self.component_definition_mRNA : "mRNA",
                        self.component_definition_sgRNA : "sgRNA",
                        self.component_definition_cds : "CDS-RNA",
                        self.component_definition_transcriptionFactor : "Transcriptional Factor",
                        self.component_definition_effector : "Effector",
                        self.component_definition_sgRNA : "sgRNA",
                        self.component_definition_engineeredTag : "Engineered Tag",
                        self.component_definition_tag : "Tag",
                        self.component_definition_startCodon: "Start Codon",
                        self.component_definition_nonCovBindingSite: "Non-Covalent Binding Site"}
        

        self.interaction_type_names = {
            self.interaction_inhibition: "Inhibition",
            self.interaction_stimulation:"Stimulation",
            self.interaction_biochemical_reaction:"Biochemical reaction",
            self.interaction_noncovalent_bonding:"Noncovalent bonding",
            self.interaction_degradation:"Degradation",
            self.interaction_genetic_production:"Genetic production",
            self.interaction_control:"Control"
        }

        self.inhibition_participants = {self.participant_inhibitor : "Inhibitor",
                                        self.participant_inhibited : "Inhibited", 
                                        self.participant_participation_promoter : "Promoter",
                                        self.participant_stimulator : "Stimulator",
                                        self.participant_stimulated : "Stimulated", 
                                        self.participant_reactant : "Reactant",
                                        self.participant_product : "Product",
                                        self.participant_modifier : "Modifier",
                                        self.participant_modified : "Modified",
                                        self.participant_template : "Template"}

        self.interaction_direction =   {self.participant_inhibitor : "in",
                                        self.participant_stimulator : "in",
                                        self.participant_modifier : "in",
                                        self.participant_reactant : "in",
                                        self.participant_participation_promoter : "in",
                                        self.participant_template : "in",
                                        self.participant_inhibited : "out",
                                        self.participant_stimulated : "out",
                                        self.participant_modified : "out",
                                        self.participant_product : "out"}

identifiers = SBOLIdentifiers()