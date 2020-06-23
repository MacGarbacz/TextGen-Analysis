from src import model
from src import generator
from src import subparser
from src import model_checkpointed
import threading


class Assembler():
    def __init__(self, grammar, checkpointed=False, threshold=0):
        self.checkpointed = checkpointed
        self.language = grammar.split("/")[-1][8:-4]
        self.generator = generator.Generator(self.language)
        self.parser = subparser.Parser(self.language)

        if checkpointed:
            self.model = model_checkpointed.ModelCheckpointed(self.language, threshold)
        else:
            self.model = model.Model(self.language)

    def execute(self, training_data_size, generated_data_size, epochs, verbose):
        self.generator.generate_sentences(training_data_size)
        self.generator.generate_structures()
        if self.checkpointed:
            accuracies = self.model.run_model(epochs, generated_data_size)
        else:
            self.model.run_model(epochs, generated_data_size)
        self.generator.generate_tagged_text()
        self.parser.parse(verbose)

        if self.checkpointed:
            return accuracies
