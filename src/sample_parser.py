from lark import Lark


class SampleParser:
    def __init__(self, language):
        self.language = language
        self.parsing_results = {}

    def parse(self):

        input_grammar_file = "../grammar/grammar_" + self.language + ".txt"

        path = '../output/generated_text_' + self.language + '_sample' + '.txt'

        # read in the grammar, create parser
        grammar = ''
        with open(input_grammar_file, "r") as f:
            for line in f:
                if not line.startswith('#'):
                    grammar = grammar + line

        f.close()
        pars = Lark(grammar, debug=True, start='sentence')

        with open(path, "r") as f:

            counter_sentence = 0
            counter_line = 0
            sentences_lengths = []
            successful_parsing_index = []

            for num, line in enumerate(f):

                contents = {}
                contents["sentence"] = line
                self.parsing_results[num] = contents

                counter_line += 1
                sentences_lengths.append(len(line.split(" ")))

                if not line:
                    break

                    # sentence
                try:
                    t = pars.parse(line)
                    # self.parsing_results[num]["correct sentence"] = 1
                    successful_parsing_index.append(counter_line)
                    counter_sentence += 1
                # if not sentence, try other possibilities
                except:
                    # self.parsing_results[num]["correct sentence"] = 0
                    continue

            score = counter_sentence / (counter_line)

            print("Number of sentences parsed: %d out of %d" % (counter_sentence, counter_line))
            print("Base accuracy =", score)

        f.close()
        return score
