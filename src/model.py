from __future__ import print_function
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import LSTM
from tensorflow.keras.optimizers import RMSprop
import numpy as np
import random
from tensorflow.keras.callbacks import ModelCheckpoint


class Model:
    def __init__(self, language):
        self.language = language

    def run_model(self, epochs, generated_text_length):
        file = '../training_data/generated_sentences_' + self.language + '.txt'
        with open(file, 'r') as f:
            text = f.read().lower()

        wordsRaw = text.split(" ")
        words = []

        for i in wordsRaw:
            if "\n" in i:
                words.append(i[1:])
            else:
                words.append(i)

        vocab = sorted(list(set(words)))

        print('total vocab:', len(vocab))
        char_indices = dict((c, i) for i, c in enumerate(vocab))
        indices_char = dict((i, c) for i, c in enumerate(vocab))

        # cut the text in semi-redundant sequences of maxlen characters
        maxlen = 40
        step = 3
        sentences = []
        next_vocab = []
        for i in range(0, len(words) - maxlen, step):
            sentences.append(words[i: i + maxlen])
            next_vocab.append(words[i + maxlen])
        print('nb sequences:', len(sentences))

        print('Vectorization...')
        x = np.zeros((len(sentences), maxlen, len(vocab)), dtype=np.bool)
        y = np.zeros((len(sentences), len(vocab)), dtype=np.bool)
        for i, sentence in enumerate(sentences):
            for t, char in enumerate(sentence):
                x[i, t, char_indices[char]] = 1
            y[i, char_indices[next_vocab[i]]] = 1

        # build the model: a single LSTM
        print('Build model...')
        model = Sequential()
        model.add(LSTM(128, input_shape=(maxlen, len(vocab))))
        model.add(Dense(len(vocab), activation='softmax'))

        # checkpoint
        filepath = "weights.best.hdf5"
        checkpoint = ModelCheckpoint(filepath, monitor='loss', verbose=1, save_best_only=False, mode='max')

        callbacks_list = [checkpoint]

        optimizer = RMSprop(learning_rate=0.01)
        model.compile(loss='categorical_crossentropy', optimizer=optimizer)

        model.fit(x, y,
                  batch_size=128,
                  epochs=epochs,
                  callbacks=callbacks_list)

        # Function to generate text with a given number of sentences, diversity parameter controls the randomness
        def generate_text(length, diversity):
            print("Generating %d sentences, please hold..." % length)
            # Get random starting text
            start_index = random.randint(0, len(words) - maxlen - 1)
            generated = []
            sentence = words[start_index: start_index + maxlen - 1]
            #print(sentence)
            # print(sentence, len(sentence))
            generated = sentence
            sentencesEncountered = 0
            while sentencesEncountered < length:
                x_pred = np.zeros((1, maxlen, len(vocab)))
                for t, char in enumerate(sentence):
                    x_pred[0, t, char_indices[char]] = 1.

                preds = model.predict(x_pred, verbose=0)[0]
                next_index = self.sample(preds, diversity)
                next_char = indices_char[next_index]
                if next_char == 'endoftext':
                    sentencesEncountered += 1
                    #print(sentencesEncountered)
                generated.append(next_char)
                sentence.append(next_char)
                sentence = sentence[1:]

            generatedText = " ".join(generated)
            return generatedText

        generated_text = generate_text(generated_text_length, 1.0)

        with open('../output/generated_text_' + self.language + '.txt', 'w') as f:
            sentencesRaw = generated_text.lower().split("endoftext")
            sentencesFixed = ''
            if len(sentencesRaw) != generated_text_length:
                diff = len(sentencesRaw) - generated_text_length - 2
                sentencesRaw = sentencesRaw[diff:]
            for i in range(1, len(sentencesRaw) - 1):
                f.write(sentencesRaw[i][1:] + 'EndOfText')
                f.write('\n')
        f.close()

    def sample(self, preds, temperature=1.0):
        # helper function to sample an index from a probability array
        preds = np.asarray(preds).astype('float64')
        preds = np.log(preds) / temperature
        exp_preds = np.exp(preds)
        preds = exp_preds / np.sum(exp_preds)
        probas = np.random.multinomial(1, preds, 1)
        return np.argmax(probas)