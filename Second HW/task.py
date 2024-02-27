import os
from bs4 import BeautifulSoup
from collections import defaultdict
from nltk.tokenize import WordPunctTokenizer
from nltk.corpus import stopwords
import pymorphy2

class Lemmatisator:
    BAD_TOKENS_TAGS = {"PREP", "CONJ", "PRCL", "INTJ", "LATN", "PNCT", "NUMB", "ROMN", "UNKN"}

    def __init__(self):
        self.stop_words = set(stopwords.words("russian"))
        self.tokenizer = WordPunctTokenizer()
        self.morph_analyzer = pymorphy2.MorphAnalyzer()
        self.tokens = set()
        self.lemmas = defaultdict(set)

    def extract_text_from_html(self, file_path):
        with open(file_path) as f:
            soup = BeautifulSoup(f.read(), features="html.parser")
        return " ".join(soup.stripped_strings)

    def process_documents(self, directory):
        for filename in os.listdir(directory):
            if filename.endswith(".html"):
                file_path = os.path.join(directory, filename)
                text = self.extract_text_from_html(file_path)
                self.tokenize_and_lemmatize(text)

    def tokenize_and_lemmatize(self, text):
        tokens = self.tokenizer.tokenize(text)
        for token in tokens:
            if (
                    token.isalpha()
                    and token not in self.stop_words
                    and not any(char.isdigit() for char in token)
            ):
                morph = self.morph_analyzer.parse(token)[0]
                if (
                        any(tag in morph.tag for tag in self.BAD_TOKENS_TAGS)
                        or morph.score < 0.5
                ):
                    continue
                lemma = morph.normal_form
                self.tokens.add(token)
                self.lemmas[lemma].add(token)

    def write_tokens_to_file(self, tokens_file_path):
        with open(tokens_file_path, "w", encoding="utf-8") as file:
            file.write("\n".join(self.tokens))

    def write_lemmas_to_file(self, lemmas_file_path):
        with open(lemmas_file_path, "w", encoding="utf-8") as file:
            for lemma, tokens in self.lemmas.items():
                file.write(f"{lemma} {' '.join(tokens)}\n")

if __name__ == "__main__":
    lm = Lemmatisator()
    lm.process_documents('../pages')
    lm.write_tokens_to_file("tokens.txt")
    lm.write_lemmas_to_file("lemmas.txt")