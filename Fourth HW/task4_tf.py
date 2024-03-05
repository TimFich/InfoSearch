import math
import os
import shutil
from collections import Counter, defaultdict
from pathlib import Path

import nltk
import pymorphy2
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from nltk.tokenize import WordPunctTokenizer

FILES_PATH = "../pages"
TOKENS_PATH = "token_tf_idf"
LEMMAS_PATH = "lemma_tf_idf"
nltk.download("stopwords")


def get_text_from_html(file_path):
    with open(file_path) as f:
        soup = BeautifulSoup(f.read(), features="html.parser")
    return " ".join(soup.stripped_strings)


def idf_word_counter(files_texts, word):
    count = sum(word in text for text in files_texts.values())
    if count > 100:
        print(word, count)
    return count


class TFIDCalculator:
    BAD_TOKENS_TAGS = {"PREP", "CONJ", "PRCL", "INTJ", "LATN", "PNCT", "NUMB", "ROMN", "UNKN"}

    def __init__(self, text):
        self.text = text
        self.stop_words = set(stopwords.words("russian"))
        self.tokenizer = WordPunctTokenizer()
        self.morph_analyzer = pymorphy2.MorphAnalyzer()
        self.tokens = set()
        self.lemmas = defaultdict(set)
        self.parse_text()

    def parse_text(self):
        tokens = self.tokenizer.tokenize(self.text)
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


if __name__ == "__main__":
    try:
        shutil.rmtree(TOKENS_PATH)
        shutil.rmtree(LEMMAS_PATH)
    except FileNotFoundError:
        pass

    os.makedirs(TOKENS_PATH, exist_ok=True)
    os.makedirs(LEMMAS_PATH, exist_ok=True)

    files_texts = {}
    for root, _, files in os.walk(FILES_PATH):
        for file in sorted(files):
            text = get_text_from_html(os.path.join(root, file))
            files_texts[file] = text

    full_text = " ".join(files_texts.values())
    full_text_calc = TFIDCalculator(full_text)
    for file_name, text in files_texts.items():
        text_cals = TFIDCalculator(text)
        words_counter = Counter(text_cals.tokenizer.tokenize(text))

        for token in text_cals.tokens:
            tf = words_counter[token] / len(text_cals.tokenizer.tokenize(text))
            idf = math.log(len(files_texts) / (1 + idf_word_counter(files_texts, token)))
            tf_idf = tf * idf
            with open(Path(TOKENS_PATH) / f"{os.path.splitext(file_name)[0]}.txt", "a") as f:
                f.write(f"{token} {idf} {tf_idf}\n")

        for lemma, tokens in text_cals.lemmas.items():
            tf_n = sum(words_counter[token] for token in tokens)
            count = sum(any(token in text for token in tokens) for text in files_texts.values())
            tf = tf_n / len(text_cals.tokenizer.tokenize(text))
            idf = math.log(len(files_texts) / (1 + count))
            tf_idf = tf * idf
            with open(Path(LEMMAS_PATH) / f"{os.path.splitext(file_name)[0]}.txt", "a") as f:
                f.write(f"{lemma} {idf} {tf_idf}\n")
