# -*- coding: utf-8 -*-
import os, glob, re
from tqdm import tqdm
from random import shuffle

class Corpus:
    def __init__(self, *args, **kwargs):
        self.files_path = kwargs["files_path"]
        self.files = glob.glob(os.path.join(self.files_path, kwargs["expression"]))
        self.files_lines = [sum(1 for line in open(file) if self._clean_line(line) is not None) for file in self.files]
        self.total_lines = sum(self.files_lines)
        self.corpus = [None] * self.total_lines
        self.corpus_pointer = 0
        self._process_files()

    def _process_files(self):
        i = 0
        pbar = tqdm(total=self.total_lines)
        round_number = int(self.total_lines / 100)
        for file in self.files:
            with open(file) as f:
                for line in f:
                    if i % round_number == 0:
                        pbar.update(round_number)
                    cleaned_line = self._clean_line(line)
                    if cleaned_line is None:
                        continue
                    self.corpus[self.corpus_pointer] = cleaned_line
                    self.corpus_pointer += 1
                    i += 1

    def _clean_line(self, line):
        # replace non valid characters
        line = re.sub(r"[^0-9A-Za-zÀ-ú\s]", "", line)
        # replace accents
        line = line.replace(u'á', r'a'). \
            replace(u'é', r'e'). \
            replace(u'í', r'i'). \
            replace(u'ó', r'o'). \
            replace(u'ú', r'u'). \
            replace(u'à', r'a'). \
            replace(u'è', r'e'). \
            replace(u'ì', r'i'). \
            replace(u'ò', r'o'). \
            replace(u'ù', r'u'). \
            replace('\t', ''). \
            replace('\r\n', ''). \
            replace('\n', '')
        # remove line break, marginal spaces and lowercase
        line = line.strip().lower()

        if line == "\n" or line == "":
            return None
        else:
            return line

    def _shuffle(self):
        shuffle(self.corpus)

    def get_next_line(self):
        if self.corpus_pointer == self.total_lines:
            self._shuffle()
            self.corpus_pointer = 0
        line = self.corpus[self.corpus_pointer]
        self.corpus_pointer += 1
        return line

    def generator(self):
        while True:
            yield self.get_next_line()

    def save(self, filename, test_percentage):
        train_lines = int(self.total_lines * (1 - test_percentage))
        with open("train_" + filename, "w") as f:
            for line in self.corpus[:train_lines]:
                f.write("%s\n" % line)

        with open("test_" + filename, "w") as f:
            for line in self.corpus[train_lines:]:
                f.write("%s\n" % line)

class Dictionary:
    def __init__(self, corpus):
        self.corpus = corpus
        self.dictionary = {}
        self._generate()

    def _generate(self):
        pbar = tqdm(total=self.corpus.total_lines)
        round_number = int(self.corpus.total_lines / 100)
        for i, line in enumerate(self.corpus.corpus):
            if i % round_number == 0:
                pbar.update(round_number)
            # tokenize
            tokens = line.split()
            for token in tokens:
                try:
                    self.dictionary[token] += 1
                except:
                    self.dictionary[token] = 1

    def as_ordered_tuples(self):
        as_tuples = []
        for key, value in self.dictionary.items():
            as_tuples.append((key, value))
        return sorted(as_tuples, key=lambda tup: tup[1], reverse=True)

    def save(self, filename):
        special_elmo_tokens = ["<S>", "</S>", "<UNK>"]
        with open(filename, "w") as f:
            for stoken in special_elmo_tokens:
                f.write("%s\n" % stoken)

            for token, frequency in self.as_ordered_tuples():
                f.write("%s\n" % token)


if __name__ == '__main__':
    corpus_config = {
        "expression": "*.txt",
        "files_path": "data/corpus"
    }

    def print_status(msg):
        len_msg = len(msg)
        line_separator = "-" * 150
        previous_space = " " * int((len(line_separator) - len_msg)/2)
        print("\n%s\n%s%s\n%s" % (line_separator, previous_space, msg.upper(), line_separator))

    print_status("creating corpus")
    c = Corpus(**corpus_config)
    #print(c.corpus[-10:])

    print_status("creating dictionary")
    d = Dictionary(c)

    #print(d.as_ordered_tuples()[:100])

    d.save("dictionary.txt")
    c.save("alemana_corpus.txt", test_percentage=0.1)

