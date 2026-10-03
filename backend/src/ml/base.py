from abc import abstractclassmethod,ABC


class BaseProcessor(ABC):
    @abstractclassmethod
    def process(self):
        return