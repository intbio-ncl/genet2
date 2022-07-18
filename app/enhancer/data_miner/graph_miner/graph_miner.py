from rdflib import URIRef,Literal

import re

resource_threshold = 10
class GraphMiner:
    def __init__(self,database_manager):
        self.database=database_manager


    def get_related_graphs(self,entity,resources=[],graph=None):
        if not isinstance(resources,(list,set,tuple)):
            resources = [resources]
        graphs = []
        if graph is not None:
            graphs.append(graph)
            resources += self._get_potential_resources(entity,graph)
        current_count = 1
        seen_resources = self._update_seen_resources(entity,[])

        while len(resources) != 0 and current_count < resource_threshold:
            resource = resources.pop(0)
            if self._seen_resource(resource,seen_resources):
                continue
            seen_resources = self._update_seen_resources(resource,seen_resources)
            graph = self.database.get(resource)
            if graph is None:
                continue
            
            resources += self._get_potential_resources(resource,graph)
            graphs.append(graph)    
            current_count += 1
        return graphs

    def get_metadata(self,graph):
        metadata = []
        metadata_predicates = self.database.get_metadata_identifiers()
        for s,p,o in graph:
            if p in metadata_predicates:
                metadata.append((s,p,o))
        return metadata

    def _get_potential_resources(self,identifier,graph):
        potential_resources = []
        for s,p,o in graph:
            if identifier != s:
                continue
            if o == identifier:
                continue

            if isinstance(o,Literal):
                o_elements = re.split(r'<|>|\s ',o)
            elif isinstance(o,URIRef):
                o_elements = [o]

            for element in o_elements:
                if not self.database.is_record(element):
                    continue
                potential_resources.append(element)
        return list(set(potential_resources))

    def _seen_resource(self,resource,seen_resources):
        if isinstance(resource,URIRef):
            if self._get_name(resource) in seen_resources:
                return True
        if str(resource) in seen_resources:
            return True
        return False

    def _update_seen_resources(self,resource,seen_resources):
        if isinstance(resource,URIRef):
            resource = self._get_name(resource)
        seen_resources.append(resource)
        return seen_resources

    def _get_name(self,subject):
        split_subject = self._split(subject)
        if len(split_subject[-1]) == 1 and split_subject[-1].isdigit():
            return split_subject[-2]
        else:
            return split_subject[-1]

    def _split(self,uri):
        return re.split('#|\/|:', uri)