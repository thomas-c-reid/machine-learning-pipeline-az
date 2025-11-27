from pipeline.steps.pipeline_step import PipelineStep

class Pipeline:
    def __init__(self):
        self.steps = []
        
    def add_step(self, pipeline_step: PipelineStep):
        self.steps.append(pipeline_step)
        
    # TODO: We might want to use batch processing here - not feed whole dataset
    def execute(self, data):
        for step in self.steps:
            data = step.process(data)
        return data
        