import re

from app.visualiser.builder.builders.design.interaction_genetic import InteractionGeneticViewBuilder
from app.visualiser.builder.builders.editor.utility import produce_aggregated_interaction_graph
from app.visualiser.builder.builders.editor.utility import produce_interaction_graph
from app.visualiser.builder.builders.editor.common_builds import build_interaction_uri
from app.visualiser.builder.builders.editor.common_builds import build_properties
from app.visualiser.builder.builders.editor.common_builds import create_consists_of
from app.graph.utility.model.model import model
from app.graph.utility.graph_objects.node import Node


class EditorInteractionGeneticViewBuilder(InteractionGeneticViewBuilder):
    def __init__(self,graph):
        super().__init__(graph)

    def build(self):
        genetic_pred = model.identifiers.objects.DNA
        g = self._subgraph(produce_interaction_graph(self._graph))
        g = produce_aggregated_interaction_graph(g,genetic_pred)
        g = self._subgraph(new_graph = g)
        return g

    def get_edge_types(self):
        return [model.identifiers.objects.repression,
                model.identifiers.objects.activation]
    
    def get_node_types(self):
        dna_p = model.identifiers.objects.dna
        c_id = model.get_class_code(dna_p)
        return [dna_p] + [k[1]["key"] for k in model.get_derived(c_id)]

    def transform(self,n,v,e):
        edges = []
        dna_o = str(model.identifiers.objects.dna)
        promoter_o = str(model.identifiers.objects.promoter)
        activation_o = str(model.identifiers.objects.activation)
        cds_o = str(model.identifiers.objects.cds)
        repression_o = str(model.identifiers.objects.repression)
        mediator_dict = {(promoter_o,activation_o,cds_o):self._pac,
                         (promoter_o,repression_o,promoter_o):self._prp,
                         (promoter_o,repression_o,cds_o):self._prc,
                         (promoter_o,activation_o,promoter_o) : self._pap,
                         (cds_o,repression_o,promoter_o) : self._crp,
                         (cds_o,repression_o,cds_o) : self._crc,
                         (cds_o,activation_o,cds_o) : self._cac,
                         (cds_o,activation_o,promoter_o) : self._cap}

        # Genetic Graphs are Multi-barpartite. 
        # Therefore, inferences must be rule based.
        n_v = list(n.values())[0]
        v_v = list(v.values())[0]
        nt = n_v.get_type()
        vt = v_v.get_type()
        if n_v.get_type() == dna_o or n_v.get_type() == dna_o:
            return self._dna(n,v,e)
        i_val = (nt,e,vt)
        if i_val not in mediator_dict:
            return edges        
        return mediator_dict[i_val](n,v,e)

    def _interaction(self,n,v,e):
        edges = []
        assert(len(n) == 1)
        assert(len(v) == 1)
        n_i_inp = list(n.keys())[0]
        v_i_out = list(v.keys())[0]
        n = list(n.values())[0]
        v = list(v.values())[0]
        node_uri = build_interaction_uri(n, v, e)
        i_node = Node(node_uri, e, **build_properties(node_uri, self._graph.name))
        edges.append((i_node, n, n_i_inp, build_properties(n_i_inp, self._graph.name)))
        edges.append((i_node, v, v_i_out, build_properties(v_i_out, self._graph.name)))
        edges += create_consists_of(i_node, self._graph.name)
        return edges

    def _dna(self,n,v,e):
        '''
        DNA -> * -> *
        Whenever DNA type is provides no inference can be made. 
        Direct Interacion
        '''
        return self._interaction(n,v,e)

    def _pac(self,promoter,cds,activation):
        '''
        Promoter -> Activation -> CDS
        Direct Interaction
        '''
        return self._interaction(promoter,cds,activation)

    def _prp(self,promoter1,promoter2,repression):
        # Case 3 - Promoter (p1) -> Repression -> Promoter (p2)
        # @@ Consideration @@ A promoter that regulates 2+ CDS, which is the repressor? 
        # Currently it will add repression from all proteins. 
        activator_p = model.identifiers.predicates.activator
        activated_p = model.identifiers.predicates.activated
        repressed_p = model.identifiers.predicates.repressed
        repressor_p = model.identifiers.predicates.repressor
        product_p = model.identifiers.predicates.product
        template_p = model.identifiers.predicates.template
        repressor_p = model.identifiers.predicates.repressor
        protein = model.identifiers.objects.protein
        gp = model.identifiers.objects.genetic_production

        edges = []
        assert(len(promoter1) == 1)
        assert(len(promoter2) == 1)
        p1 = list(promoter1.values())[0]
        p2 = list(promoter2.values())[0]
        existing = [e.n for e in self._graph.get_interactions(p2,repressed_p)]
        existing = [e.v for e in self._graph.get_interaction_elements(existing,repressor_p)]
        # Does P activate a CDS?
        promoter_1_is = self._graph.get_interactions(p1,activator_p)
        if promoter_1_is == []:
            # No inference can be made. 
            # Unable to infer what promoter is regulating.
            return edges
        for p in promoter_1_is:
            i_eles = self._graph.get_interaction_elements(p.n,activated_p)
            assert(len(i_eles) == 1)
            cds = i_eles[0].v
            # Does C Produce a Protein?
            cds_ints = self._graph.get_interactions(cds,template_p)
            if cds_ints == []:
                # No -> Create Protein -> Create Protein Production.
                protein = _build_protein(cds.get_key())
                protein_d = {product_p : protein}
                cds = {template_p : cds}
                edges += self._interaction(cds,protein_d,gp)
            else:
                assert(len(cds_ints) == 1)
                i_eles = self._graph.get_interaction_elements(cds_ints[0].n,product_p)
                assert(len(i_eles) == 1)
                protein = i_eles[0].v 
            # Does Protein already repress promoter2
            if protein in existing:
                continue
            protein = {repressor_p: protein}
            # Create Prot -> Repression -> P2
            edges += self._interaction(protein,promoter2,repression)
        return edges

    def _prc(self):
        # Case 4 - Promoter -> Repression -> CDS
        # Same as Case 3
        pass
    
    def _pap(self):
        # Case 5 - Promoter -> Activation -> Promoter 
        # ??
        pass
    
    def _crp(self):
        # Case 6 - CDS (C1) -> Repression -> Promoter (P1)
        # Does CDS generate protein?
        # No - Create protein + genetic production
        # Create Protein -> Repression -> Promoter
        pass

    def _crc(self):
        # Case 7 - CDS (C1) -> Repression -> CDS (C2)
        # Same as case 6
        pass

    def _cac(self):
        # Case 8 - CDS (C1) -> Activation -> CDS (C2)
        # ??
        pass

    def _cap(self):
        # Case 9 - CDS (C1) -> Activation -> Promoter (P1)
        # ??
        pass

def _build_protein(uri):
    return Node(f'{_get_namespace(uri)}{_get_name(uri)}p/1',
                model.identifiers.objects.protein)

def _get_namespace(n):
    return n.split(_get_name(n))[0]

def _get_name(subject):
    split_subject = _split(subject)
    if len(split_subject[-1]) == 1 and split_subject[-1].isdigit():
        return split_subject[-2]
    elif len(split_subject[-1]) == 3 and _isfloat(split_subject[-1]):
        return split_subject[-2]
    else:
        return split_subject[-1]

def _split(uri):
    return re.split('#|\/|:', uri)

def _isfloat(x):
    try:
        float(x)
        return True
    except ValueError:
        return False