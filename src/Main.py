from src import assembler

my_assembler = assembler.Assembler("../grammars/grammar_alphaAAB.txt", False, 1.0)

my_assembler.execute(2000, 10, 2, True)