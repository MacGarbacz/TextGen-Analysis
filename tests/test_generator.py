import unittest
from src import generator
import os.path


class TestGenerator(unittest.TestCase):
    language = "test"
    test_path = "../training_data/generated_sentences_" + language + ".txt"

    def test_generating_sentences(self):

        test_generator = generator.Generator(self.language)
        test_generator.generate_sentences(1)

        result = os.path.exists(self.test_path)

        self.assertTrue(result)

        if result:
            os.remove(self.test_path)

    def test_generating_structures(self):

        test_generator = generator.Generator(self.language)
        test_generator.generate_structures()

        structures = ["np", "vp", "pp"]

        for structure in structures:

            structure_file_path = "../grammar/structures/generated_" + structure + "_" + self.language + ".txt"

            result = os.path.exists(structure_file_path)

            self.assertTrue(result)

            if result:
                os.remove(structure_file_path)

if __name__ == '__main__':
    unittest.main()
