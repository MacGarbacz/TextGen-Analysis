import unittest

from src import assembler

class TestAssembler(unittest.TestCase):
    def test_proper_initialization(self):
        # Test that all components are initialized for the desired language

        language = "test"

        test_assembler = assembler.Assembler(language)

        self.assertEqual(test_assembler.generator.language, language)
        self.assertEqual(test_assembler.model.language, language)
        self.assertEqual(test_assembler.parser.language, language)

    def test_incorrect_initalization(self):
        # Test behaviour when the language of choice doesn't exist
        language = "incorrect_language"

        with self.assertRaises(FileNotFoundError):
            assembler.Assembler(language)

if __name__ == '__main__':
    unittest.main()
