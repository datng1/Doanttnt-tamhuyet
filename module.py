import math
import re
import json
import collections
import nltk
from collections import Counter
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk import pos_tag
from nltk.corpus import wordnet

nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')

stop_words = set(stopwords.words('english'))

def get_wordnet_pos(treebank_tag):
    if treebank_tag.startswith('J'):
        return wordnet.ADJ
    elif treebank_tag.startswith('V'):
        return wordnet.VERB
    elif treebank_tag.startswith('N'):
        return wordnet.NOUN
    elif treebank_tag.startswith('R'):
        return wordnet.ADV
    else:
        return wordnet.NOUN

def convert_todict(text, min_freq=1):
    lemmatizer = WordNetLemmatizer()
    # Thay thế mọi ký tự không phải chữ bằng khoảng trắng
    text = re.sub(r'[^a-zA-Z]', ' ', text)
    text = text.lower()
    words_list = re.split(r'\s+', text.strip())

    pos_tagged_words = pos_tag([word.lower() for word in words_list])
    normalized_words = [
        lemmatizer.lemmatize(word, get_wordnet_pos(tag)) for word, tag in pos_tagged_words
    ]
    filtered_words = [
        word for word in normalized_words if word not in stop_words and word != ''
    ]

    word_count = Counter(filtered_words)
    filtered_word_count = {
        word: count for word, count in word_count.items() if count >= min_freq
    }
    return filtered_word_count

def merge(dict1, dict2):
    res = dict1.copy()
    if dict2 is None:
        return res
    for key, val in dict2.items():
        res[key] = res.get(key, 0) + val
    return res

def modify_paper(record, folder):
    with open(f"data/{folder}/idfsigir{folder}.json", "r") as f:
        idf_data = json.load(f)

    if record.get("abstract") is not None:
        abstract_text = " ".join([f"{word} " * freq for word, freq in record["abstract"].items()])
        word_dict = merge(convert_todict(abstract_text), convert_todict(record["title"]))
    else:
        word_dict = convert_todict(record["title"])

    max_f = max(word_dict.values()) if word_dict else 1
    for word in word_dict:
        word_dict[word] = (word_dict[word] / max_f) * idf_data.get(word, 1.0)

    return {"title": record["title"], "vector": word_dict, "label" : record["label"]}

def toidfConfer(folder):
    input_path = f"data/{folder}/pre_process_{folder}.json"
    output_path = f"data/{folder}/idfsigir{folder}.json"

    with open(input_path, "r") as f:
        data = json.load(f)

    dict_words = dict()
    for record in data:
        if record.get("abstract") is not None:
            abstract_text = " ".join([f"{word} " * freq for word, freq in record["abstract"].items()])
            word_dict = merge(convert_todict(abstract_text), convert_todict(record["title"]))
        else:
            word_dict = convert_todict(record["title"])

        for word in word_dict:
            dict_words[word] = dict_words.get(word, 0) + 1

    total_docs = len(data)
    for word in dict_words:
        dict_words[word] = 1 + math.log10(total_docs / dict_words[word])

    with open(output_path, "w") as f:
        json.dump(dict_words, f, indent=4)

def normalisation(folder):
    input_path = f"data/{folder}/data_{folder}.json"
    tfidf_path = f"data/{folder}/idfsigir{folder}.json"
    output_path = f"data/{folder}/Normalisation.json"

    with open(input_path, "r") as input_file:
        data = json.load(input_file)

    with open(tfidf_path, "r") as tfidf_file:
        tfidf = json.load(tfidf_file)

    for item in data:
        for key in tfidf:
            item['vector'].setdefault(key, 0)
        item['vector'] = collections.OrderedDict(sorted(item['vector'].items()))

    with open(output_path, "w") as output_file:
        json.dump(data, output_file, indent=4)
