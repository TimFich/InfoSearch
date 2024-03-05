import os
from collections import defaultdict
from importlib import util

FILES_DIRECTORY = "../pages"
INVERTED_INDEX_PATH = "indexes.txt"


class InvertedIndexGenerator:
    def __init__(self):
        self.inverted_index = defaultdict(list)

    def generate_inverted_index(self):
        for root, _, files in os.walk(FILES_DIRECTORY):
            for index, file_name in enumerate(sorted(files), 1):
                lemmatizer = lemmatization_module.Lemmatisator()
                lemmatizer.tokenize_and_lemmatize(
                    lemmatizer.extract_text_from_html(os.path.join(root, file_name))
                )
                for lemma in lemmatizer.lemmas.keys():
                    self.inverted_index[lemma].append(index)

    def write_inverted_index_to_file(self, path):
        with open(path, "w") as file:
            for word, inverted_array in self.inverted_index.items():
                index_info = {
                    "count": len(inverted_array),
                    "inverted_array": inverted_array,
                    "word": word,
                }
                file.write(str(index_info) + "\n")

def load_lemmatization_module(module_name, file_path):
    module_spec = util.spec_from_file_location(module_name, file_path)
    module = util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)
    return module


lemmatization_module = load_lemmatization_module(
    "Second HW", "../Second HW/task.py"
)

if __name__ == "__main__":
    inverted_index_generator = InvertedIndexGenerator()
    inverted_index_generator.generate_inverted_index()
    inverted_index_generator.write_inverted_index_to_file(INVERTED_INDEX_PATH)