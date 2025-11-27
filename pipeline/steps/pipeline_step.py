from abc import ABC, abstractmethod
 
class PipelineStep(ABC):
    def __init__(self, name: str):
        self.name = name
        
    @abstractmethod
    def process(self, data):
        """
        Function to perform some operation on dataset
        """
        
    def __repr__(self):
        return f'PipelineStep(name={self.name})'