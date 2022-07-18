from app.graph.utility.graph_objects.edge import Edge
from app.graph.utility.model.model import model

confidence = str(model.identifiers.external.confidence)
class TruthGraph:
    def __init__(self,driver):
        self.name = "truth_graph"
        self.driver = driver
        self._scm = 5
        self._upper_threshold = 100
        self._lower_threshold = 0

    def positive(self,edges):
        return self._change(edges,self._scm)
    
    def negative(self,edges):
        return self._change(edges,-self._scm)

    def get(self,edge):
        res = self.driver.edge_query(e=edge,e_props={"graph_name":self.name})
        if len(res) == 0:
            return None
        assert(len(res) == 1)
        res = res[0]
        res.replace({confidence : int(res[confidence])})
        return res

    def get_properties(self,node):
        pass
    
    def _change(self,edges,modifier):
        if not isinstance(edges,(list,set,tuple)):
            edges = [edges]
        for edge in edges:
            if not isinstance(edge,Edge):
                raise ValueError(f'{edge} must be an edge.')
            eq = self.get(edge)
            if eq is not None:
                self._update_confidence(eq,modifier)
                continue
            nq = self.driver.node_query([edge.n,edge.v],graph_name=self.name)
            if nq != []:
                assert(edge.n in nq or edge.v in nq)
                if edge.n not in nq:
                    self._add_node(edge.n)
                if edge.v not in nq:
                    self._add_node(edge.n)
                self._add_edge(edge,modifier)
            else:
                self._add_edge(edge,modifier)

    def _add_edge(self,edge,modifier):
        if modifier < 0:
            return
        e = self._add_gn(edge)
        e.update({confidence:modifier})
        self.driver.add_edge(e.n,e.v,e,mode="duplicate")
        self.driver.submit()

    def _add_node(self,node):
        node.update({"graph_name" : self.name})
        self.driver.add_node(node,mode="duplicate")
        self.driver.submit()

    def _update_confidence(self,edge,modifier):
        conf = edge.get_properties()[confidence]
        new_conf = int(conf) + modifier
        if new_conf >= self._upper_threshold:
            self._upper_threshold_map(edge)
        elif new_conf <= self._lower_threshold:
            self._lower_threshold_map(edge)
        else:
            props = {confidence : new_conf}
            self.driver.set_edge(edge,props)
            self.driver.submit()
    
    def _lower_threshold_map(self,edge):
        self._add_gn(edge)
        nedges = self.driver.edge_query(n=edge.n,directed=False)
        vedges = self.driver.edge_query(n=edge.v,directed=False)
        if len(nedges) == 1:
            self.driver.remove_node(edge.n)
        if len(vedges) == 1:
            self.driver.remove_node(edge.v)
        self.driver.remove_edge(edge)
        self.driver.submit()

    def _upper_threshold_map(self,edge):
        ids = model.identifiers
        tm = {str(ids.external.synonym) : self._upper_threshold_synonym,
             str(ids.external.type) : self._upper_threshold_type}
        if edge.get_type() in tm:
            tm[edge.get_type()](edge)

    def _upper_threshold_type(self,edge):
        pcc = model.get_class_code(edge.n.get_type())
        if model.is_derived(edge.v.get_type(),pcc):
            self.driver.remove_edge(edge)
            if len(self._edge_query(n=edge.v,directed=False)) == 1:
                self.driver.remove_node(edge.v,True)
            self.driver.add_node_label(edge.n,edge.v.get_key())
            self.driver.submit()
        else:
            print(f"""WARN:: {edge} has been tagged as reaching threshold. 
            However, {edge.v.get_type()} & {edge.n.get_type()} are exclusive tags.""")

    def _upper_threshold_synonym(self,edge):
        self.driver.merge_nodes(edge)
        
    def _add_gn(self,edge):
        gnd = {"graph_name" : self.name}
        edge.n.update(gnd)
        edge.v.update(gnd)
        edge.update(gnd)
        return edge

    def _edge_query(self,n=None,v=None,e=None,**kwargs):
        return self.driver.edge_query(n=n,v=v,e=e,e_props={"graph_name":self.name},**kwargs)        

     