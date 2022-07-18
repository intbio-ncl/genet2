from collections import MutableMapping

import re

from urllib.error import URLError
from graph.knowledge.utility.identifiers import identifiers
from graph.knowledge.data_miner.language.analyser import LanguageAnalyser
from graph.knowledge.data_miner.database.handler import DatabaseHandler
from graph.knowledge.data_miner.ontology.handler import OntologyHandler
from graph.knowledge.data_miner.graph_miner.graph_miner import GraphMiner


class DataMiner:
    def __init__(self,offline=False):
        self.language = LanguageAnalyser()
        self.database = DatabaseHandler(offline=offline)
        self.ontology = OntologyHandler(offline=offline)
        self.graph_miner = GraphMiner(self.database)


    def get_descriptor_aliases(self,descriptor):
        """Finds aliases for ontology descriptors.
        Args:
            descriptor: The descriptor URI. 
        Returns:
            List of definite aliases, list of potential aliases.
        """
        d_aliases,p_aliases = self.ontology.get_synonyms(descriptor)
        d_aliases = self.language.get_aliases(d_aliases)
        p_aliases = self.language.get_aliases(p_aliases)
        return d_aliases+p_aliases

    def get_entity_aliases(self,entity,resources=[],graph=None):
        """Finds aliases for a biological entity.
        Args:
            entity: The biological entity URI.
            graph : Optional rdf graph to extract data.
        Returns:
            List of definite aliases, list of potential aliases.
        """
        graphs = self.graph_miner.get_related_graphs(entity,resources,graph)
        texts = [self._get_name(entity)]
        triples = [t for graph in graphs for t in self.graph_miner.get_metadata(graph)]
        aliases = self.language.get_aliases(texts,triples=triples)
        return aliases


    def get_entity_descriptions(self,entity,resources=[], graph=None):
        """Finds descriptions for a biological entity
        Args:
            entity: The biological entity URI.
            graph : Optional rdf graph to extract data.
        Returns:
            List of definite descriptions, list of potential descriptions.
        """
        graphs = self.graph_miner.get_related_graphs(entity,resources,graph)
        texts = [self._get_name(entity)]
        triples = [t for g in graphs for t in self.graph_miner.get_metadata(graph)]
        descriptions = self.language.get_descriptions(texts,triples=triples)
        return descriptions


    def get_entity_descriptors(self,entity,descriptions):
        """Finds ontology terms describing the given biological entity.
        Args:
            entity: The biological entity URI.
            graph : A list of descriptions of the biological entity.
        Returns:
            List of definite descriptors, list of potential descriptors.
        """
        if len(descriptions) == 0:
            print(f"WARN:: {entity} have been provided to get_entity_descriptor with no descriptions.")
            return []
        d_descriptors,p_descriptors = self.ontology.get_descriptor(descriptions)
        return d_descriptors,p_descriptors
        
    def apply_mask(self,identifier):
        return self.ontology.mask(identifier)

    def remove_mask(self,identifier):
        return self.ontology.unmask(identifier)


    def _get_name(self,entity):
        return self._split_name(entity)


    def _split_name(self,subject):
        split_subject = self._split(subject)
        if len(split_subject[-1]) == 1 and split_subject[-1].isdigit():
            return split_subject[-2]
        else:
            return split_subject[-1]

    def _split(self,uri):
        return re.split('#|\/|:', str(uri))