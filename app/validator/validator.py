from app.validator.pipelines.comparison import comparison_pipeline 
from app.validator.pipelines.semantic import semantic_pipeline 
from app.validator.pipelines.transitive import transitive_pipeline

class Validator:
    def __init__(self,graph):
        self.graph = graph
        self.pipelines = [comparison_pipeline,
                          semantic_pipeline,
                          transitive_pipeline]
    
    def validate(self,filename):
        v_outs = {}
        self.graph.add_design(filename)
        for pipeline in self.pipelines:
            v_outs[pipeline.__class__.__name__] = pipeline(self.graph)