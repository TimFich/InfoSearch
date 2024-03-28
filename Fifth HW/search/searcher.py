import ast
import os
from pathlib import Path

import pymorphy2
from nltk.corpus import stopwords
from nltk.tokenize import WordPunctTokenizer

BASE_DIR = Path(__file__).resolve().parent.parent
INDEX_FILE_PATH = BASE_DIR.parent.joinpath("pages").joinpath("index.txt")
TF_IDF_FILES_DIR = BASE_DIR.parent.joinpath("Fourth HW").joinpath("lemma_tf_idf")
INVERTED_INDEX_FILE_PATH = BASE_DIR.parent.joinpath("Third HW").joinpath("indexes.txt")


class Searcher:
    BAD_TOKENS_TAGS = {"PREP", "CONJ", "PRCL", "INTJ", "LATN", "PNCT", "NUMB", "ROMN", "UNKN"}

    def __init__(self) -> None:
        self.stop_words = set(stopwords.words("russian"))
        self.tokenizer = WordPunctTokenizer()
        self.morph_analyzer = pymorphy2.MorphAnalyzer()
        self.pages = self.get_pages(INDEX_FILE_PATH)
        self.lemmas = self.get_all_lemmas(INVERTED_INDEX_FILE_PATH)
        self.tf_idf_matrix = self.get_tf_idf_matrix(TF_IDF_FILES_DIR)

    def get_lemmas(self, query):
        lemmas = list()
        for token in set(self.tokenizer.tokenize(query)):
            morph = self.morph_analyzer.parse(token)
            if (
                any([x for x in self.BAD_TOKENS_TAGS if x in morph[0].tag])
                or token in self.stop_words
            ):
                continue
            if morph[0].score >= 0.4:
                lemmas.append(morph[0].normal_form)
        return lemmas

    def get_pages(self, path):
        pages = {}
        with open(path) as f:
            for line in f.readlines():
                parts = line.split(maxsplit=2)
                key, value = f"page_{parts[0].replace(':', '')}.html", parts[1]
                pages[key] = value
        return pages

    def get_all_lemmas(self, path):
        lemmas = set()
        with open(path) as f:
            for line in f.readlines():
                lemmas.add(ast.literal_eval(line)["word"])
        return list(lemmas)

    def get_tf_idf_matrix(self, path):
        matrix = dict()
        for root, _, files in os.walk(path):
            for file in files:
                with open(os.path.join(root, file)) as f:
                    matrix[file] = {lemma: 0.0 for lemma in self.lemmas}
                    for line in f.readlines():
                        lemma, _, tf_idf = line.split(maxsplit=2)
                        matrix[file][lemma] = float(tf_idf)
        return matrix

    def get_query_vector(self, lemmas):
        vector = {lemma: 0 for lemma in self.lemmas}
        for lemma in lemmas:
            vector[lemma] = 1
        return vector

    def vector_normalize(self, vector):
        return sum([c**2 for c in vector]) ** 0.5

    def calculate_cosine_similarity(self, query_vector, page_vector):
        dot = sum(q * p for q, p in zip(query_vector, page_vector))
        if dot:
            return dot / (
                self.vector_normalize(query_vector) * self.vector_normalize(page_vector)
            )
        return 0

    def get_similarities(self, query_vector):
        similarities = {}
        for page, lemma_tf_idf in self.tf_idf_matrix.items():
            page_vector = list(lemma_tf_idf.values())
            similarity = self.calculate_cosine_similarity(query_vector, page_vector)
            if similarity:
                similarities[page.replace('.txt', '.html')] = similarity
        return sorted(
            [(self.pages[x[0]], x[1]) for x in similarities.items() if x[1] > 0.0],
            key=lambda x: x[1],
            reverse=True,
        )

    def search(self, query):
        query_lemmas = self.get_lemmas(query)
        query_vector = self.get_query_vector(query_lemmas)
        return self.get_similarities(list(query_vector.values()))


query_searcher = Searcher()
