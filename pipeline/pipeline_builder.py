from pipeline.pipeline import Pipeline
from pipeline.steps import PipelineStep, CleanDataStep, CategoricalEncodeStep, NormalisationStep, FeatureEngineeringStep
from dotenv import load_dotenv
import os

load_dotenv()

class PipelineBuilder:
    
    def __init__(self, steps_list):
        self.pipeline_steps: list = steps_list
        
    def load_step(self, step_name: str) -> PipelineStep:
        # We want to have a function for loading in an instance of each step
        if step_name == 'CleanDataStep':
            return CleanDataStep()
        if step_name == 'FeatureEngineeringStep':
            return FeatureEngineeringStep()
        if step_name == 'CategoricalEncodeStep':
            return CategoricalEncodeStep()
        if step_name == 'NormalisationStep':
            return NormalisationStep()

        
    def build_pipeline(self) -> Pipeline:
        pipeline = Pipeline()

        for step_name in self.pipeline_steps:
            step = self.load_step(step_name)
            if step is None:
                # skip unknown steps but inform the caller
                continue
            pipeline.add_step(step)

        return pipeline