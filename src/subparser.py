from lark import Lark
import copy
import csv


class Parser:
    def __init__(self, language):
        self.language = language
        self.parsing_results = {}

    def parse(self, verbose):

        input_grammar_file = "../grammar/grammar_" + self.language + ".txt"

        path = '../output/generated_text_' + self.language + '.txt'
        files = [path]
        print("\nTesting for version :: *" + self.language + "*" + "\n")

        # read in the grammar, create parser
        grammar = ''
        with open(input_grammar_file, "r") as f:
            for line in f:
                if not line.startswith('#'):
                    grammar = grammar + line

        pars = Lark(grammar, debug=True, start='sentence')

        for input_sentences_file in files:
            # read grammar, filter out comment lines (starting with #)d

            # process input file
            with open(input_sentences_file, "r") as f:

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
                        #self.parsing_results[num]["correct sentence"] = 1
                        successful_parsing_index.append(counter_line)
                        counter_sentence += 1
                    # if not sentence, try other possibilities
                    except:
                        #self.parsing_results[num]["correct sentence"] = 0
                        continue

                print("Number of sentences parsed: %d out of %d" % (counter_sentence, counter_line))
                print("Base accuracy =", counter_sentence / (counter_line))

                unsuccessful_sentences_index = []
                unsuccessful_sentences_lengths = []
                successful_sentences_lengths = []

                for i in range(counter_line):
                    if i not in successful_parsing_index:
                        unsuccessful_sentences_index.append(i)
                        unsuccessful_sentences_lengths.append(sentences_lengths[i])
                    else:
                        successful_sentences_lengths.append(sentences_lengths[i])




                for i in range(counter_line):
                    if i not in successful_parsing_index:
                        unsuccessful_sentences_index.append(i)

                self.partial_parse(unsuccessful_sentences_index)

                with open("../output/parsing_results_" + self.language + ".csv", 'w', newline='') as f:
                    headers_written = False
                    for sentence in self.parsing_results.keys():
                        temp_dict = self.parsing_results[sentence]
                        w = csv.DictWriter(f,temp_dict.keys())
                        if not headers_written:
                            w.writeheader()
                            headers_written = True
                        w.writerow(temp_dict)
                #print(self.parsing_results)

    def partial_parse(self, index_array):

        tagged_lines = []

        with open("../output/tagged_text_" + self.language + ".txt", 'r') as f:
            for num, line in enumerate(f):
                tagged_lines.append(line)

        f.close()

        # Read in other files
        substructures = {}

        types = ["np", "vp", "pp"]

        for t in types:
            substructures[t] = []
            with open("../grammar/structures/generated_" + t + "_" + self.language + ".txt", 'r') as f:
                for num, line in enumerate(f):
                    substructures[t].append(line[:-2])
            f.close()

        score = 0
        counter = 0
        for line in tagged_lines:
            if counter not in index_array:
                self.parsing_results[counter]["np"] = []
                self.parsing_results[counter]["vp"] = []
                self.parsing_results[counter]["pp"] = []
                self.parsing_results[counter]["score"] = 1.0
                score += 1
                counter += 1
            else:
                temp_score, structures_found = self.partial_credit_parse(line, substructures)
                #Append extra details
                self.parsing_results[counter]["np"] = structures_found["np"]
                self.parsing_results[counter]["vp"] = structures_found["vp"]
                self.parsing_results[counter]["pp"] = structures_found["pp"]
                self.parsing_results[counter]["score"] = temp_score

                score += temp_score
                counter += 1

        print("Accuracy including partial credit: " + str(score / len(tagged_lines)))



    def filter_for_unique(self, structure_indecies):
        unique_structures = []
        remaining = copy.deepcopy(structure_indecies)

        while len(remaining) != 0:
            longest_structure_len = 0
            longest_structure = (0, 0)
            for indecies in remaining:
                if (indecies[1] - indecies[0]) > longest_structure_len:
                    longest_structure = indecies
                    longest_structure_len = indecies[1] - indecies[0]

            remaining.remove(longest_structure)
            unique_structures.append(longest_structure)

            for i in range(len(structure_indecies)):
                current_tupule = structure_indecies[i]
                if current_tupule != longest_structure:
                    if current_tupule[0] == longest_structure[0] or current_tupule[0] in range(longest_structure[0],
                                                                                               longest_structure[
                                                                                                   1]):
                        remaining.remove(current_tupule)

        return unique_structures

    def partial_credit_parse(self, line, substructures):

        structures_found = {}
        structures_found["np"] = []
        structures_found["vp"] = []
        structures_found["pp"] = []

        temporary_structures_found = {}
        temporary_structures_found["np"] = []
        temporary_structures_found["vp"] = []
        temporary_structures_found["pp"] = []

        parsing_result = []
        for structure_type in substructures.keys():
            structures_found[structure_type] = []
            structure_indecies = []
            for structure in substructures[structure_type]:
                if structure in line:
                    # print(line, structure, structure_type)
                    index = line.index(structure)
                    temporary_structures_found[structure_type].append([structure, (index, index + len(structure))])
                    structure_indecies.append((index, index + len(structure)))

            unique_structures = self.filter_for_unique(structure_indecies)
            for identified_structure in temporary_structures_found[structure_type]:
                for unique_structure in unique_structures:
                    #print(identified_structure[1], unique_structure[0])
                    if identified_structure[1] == unique_structure:
                        structures_found[structure_type].append(identified_structure[0])
            for structure in unique_structures:
                parsing_result.append(structure_type)
            #print(structure_type, structure_indecies, unique_structures)
            #print(structure_type, len(temporary_structures_found[structure_type]), len(structures_found[structure_type]))

        score = 0
        sentence_length = len(line.split(" "))
        for structure in parsing_result:
            if structure == 'pp':
                score += 0.5
            if structure == 'np':
                score += 1
            if structure == 'vp':
                score += 1.5
        score = score / sentence_length

        # print(score)
        return score, structures_found
