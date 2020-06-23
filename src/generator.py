import re
import random
from operator import itemgetter


class Generator:
    def __init__(self, language):
        self.language = language
        self.input_grammar_file = "../grammar/grammar_" + language + ".txt"
        self.grammar = self.populate_grammar()

    def generate_sentences(self, number):
        output_sentence_file = "../training_data/generated_sentences_" + self.language + ".txt"

        print("\nBuilding sentences from grammar :: *" + self.language + "*" + "\n")

        with open(output_sentence_file, 'w') as f:
            for i in range(number):
                f.write(self.linearize_phrase(self.build_phrase('sentence'), 'word'))
                f.write('\n')
        f.close()
        print("Completed generating %d sentences for the language %s " % (number, self.language))

    def generate_structures(self):
        print("\nBuilding structures from grammar :: *" + self.language + "*" + "\n")

        # Generate all the possible structures within the list
        structures = ["np", "vp", "pp"]

        # Structures in the list will be generated randomly and then filtered for unique structures
        for structure in structures:
            output_structure_file = "../grammar/structures/generated_" + structure + "_" + self.language + ".txt"
            with open(output_structure_file, 'w') as f:
                generated = []
                for i in range(20000):
                    generated.append(self.linearize_phrase(self.build_phrase(structure), 'type'))
                unique_structures = set(generated)
                for unique_structure in unique_structures:
                    f.write(unique_structure)
                    f.write("\n")

            f.close()
        print("Completed generating structures for the language %s " % self.language)

    def generate_tagged_text(self):

        vocab = {}

        for wordtype in self.grammar["word"].keys():
            vocab[wordtype] = []
            for word in self.grammar["word"][wordtype]:
                vocab[wordtype].append(word[1:-1])

        # Open the file and read in the lines
        lines = []

        with open("../output/generated_text_" + self.language + ".txt", 'r') as f:
            for num, line in enumerate(f):
                lines.append(line.split(" "))

        f.close()

        # Create tagging for the text using the vocabulary

        tagged_lines = []

        wordtypes = vocab.keys()

        for line in lines:

            line_tagged = []

            for word in line:
                for wordtype in wordtypes:
                    if word in vocab[wordtype]:
                        line_tagged.append(wordtype)

            tagged_lines.append(line_tagged)

        with open("../output/tagged_text_" + self.language + ".txt", 'w') as f:
            for line in tagged_lines:
                f.write(" ".join(line))
                f.write(" \n")

        f.close()

    # Helper functions

    def populate_grammar(self):
        # read grammar, filter out comment lines (starting with #)d
        grammar = {}
        grammar['phrase'] = {}
        grammar['word'] = {}

        with open(self.input_grammar_file, "r") as f:
            for line in f:
                # Find the highest level rule
                if re.search('\#\?start:', line):
                    line = line.split(sep=': ')
                    grammar['start'] = line[1].rstrip()
                    continue
                # But skip any other commented lines

                elif line.startswith('#'):
                    continue

                # Node labels contain : as definition
                elif re.search(':', line):
                    line = line.split(sep=': ')
                    # lowercase labels are phrase nodes;
                    # uppercase labels are terminal nodes
                    if re.search('[a-z]', line[0]):
                        nodeType = 'phrase'
                    else:
                        nodeType = 'word'

                    node = line[0]
                    expansion = [line[1].rstrip()]
                    grammar[nodeType][node] = expansion

                    # Continuations of node labels start with |;
                    # nodeType and node values hold over from however many lines
                    # previous they were defined

                elif re.search('\|', line):
                    line = line.split(sep='|')
                    expansion.append(line[1].rstrip())
                else:
                    continue
                grammar[nodeType][node] = expansion
        f.close()
        return grammar

    def build_phrase(self, node):
        tree = {}
        nodes = random.choice(self.grammar['phrase'][node]).split(sep=' _W_ ')
        ix = 1
        for n in nodes:
            tagged_n = n + '.' + str(ix)
            tree[tagged_n] = {}
            if re.search('^[a-z]', n):
                # strip out tag for looking up rule
                tree[tagged_n]['phrase'] = self.build_phrase(n)
            else:
                tree[tagged_n]['word'] = random.choice(self.grammar['word'][n])
                tree[tagged_n]['word'] = re.sub('\"', '', tree[tagged_n]['word'])
            tree[tagged_n]['position'] = ix
            tree[tagged_n]['type'] = n
            ix += 1
        return (tree)

    def linearize_phrase(self, tree, mode):
        sentence = ''
        components = []
        for phrase in tree.keys():
            node = [phrase, tree[phrase]['position']]
            components.append(node)

        components.sort(key=itemgetter(1))
        for node in components:
            if re.search('[A-Z]', node[0]):
                sentence = sentence + tree[node[0]][mode] + ' '
            else:
                sentence = sentence + self.linearize_phrase(tree[node[0]]['phrase'], mode)

        return (sentence)
