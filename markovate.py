import random

class Markovator:

    def __init__(self):
        self.words = {}
        self.starting_entry = {'word': None, 'following_words':[]}

    def add_to_entry(self, word, entry):
        existing_following_words = filter(lambda following_word: following_word['word'] == word, entry['following_words'])

        if len(existing_following_words) == 0:
            entry['following_words'].append({'word': word, 'count': 1})
        else:
            existing_following_words[0]['count'] += 1

    def flatten_entry(self, entry):
        flattened_following_words = map(lambda following_word : [following_word['word'] for x in range(0, following_word['count'])] , entry['following_words'])
        return [item for sublist in flattened_following_words for item in sublist]

    def markovate(self):
        current_reply_word = random.choice(self.flatten_entry(self.starting_entry))
        markovation = ""
        while not current_reply_word == None:
            markovation += current_reply_word + " "
            current_reply_word = random.choice(self.words[current_reply_word]['following_words'])['word']

        return markovation

    def parse_sentence(self, sentence):
        new_words = sentence.lstrip().rstrip().split(' ')    
        if len(new_words) > 0:
            previous_word = new_words.pop(0)
            self.add_to_entry(previous_word, self.starting_entry)

            for word in new_words:
                if not previous_word in self.words:
                    self.words[previous_word] = {'word': previous_word, 'following_words':[]}

                if len(word) > 0:
                    self.add_to_entry(word, self.words[previous_word])
                    previous_word = word

            if not previous_word in self.words:
                self.words[previous_word] = {'word': previous_word, 'following_words':[]}

                self.add_to_entry(None, self.words[previous_word])

    def parse_sentences(self, sentences):
        for sentence in sentences:
            self.parse_sentence(sentence)
