class PipelineLogger:
    def __init__(self):
        self.logs = {}

    def add_log(self,key,log):
        self.logs[key] = log

    def build(self):
        return self.logs
