from nltk.stem import PorterStemmer
from nltk.tokenize import RegexpTokenizer
from experta import *
import data_prep as data
from nltk.corpus import stopwords
import nltk
from collections import Counter

nltk.download('stopwords')

ps = PorterStemmer()
stop_words = set(stopwords.words('english'))
tokenizer = RegexpTokenizer(r'\w+')

patterns, all_symptoms = data.load_data()

def process_user_input(user_input):
    tokens = tokenizer.tokenize(user_input)
    filtered_tokens = [word for word in tokens if word not in stop_words]

    stemmed_tokens = []
    for w in filtered_tokens:
        w = w.replace("_", " ")
        w = ps.stem(w)
        stemmed_tokens.append(w)

    return stemmed_tokens


def match_symptoms(stemmed_tokens, stemmed_dict):
    matched_symptoms = []
    for stemmed_key, original_symptom in stemmed_dict.items():
        if stemmed_key.issubset(stemmed_tokens):
            matched_symptoms.append(original_symptom)
    return matched_symptoms


def no_matched_symptoms(matched_symptoms):
    if len(matched_symptoms) == 0:
        print("\nSorry, I could not recognize any symptoms from what you described.")
        print("Please try to describe your symptoms more clearly.")
        print("Example: 'I have itching, skin rash and fever'")
    return True


def extract_symptoms(user_input, stemmed_dict):
    stemmed_tokens = process_user_input(user_input)
    matched_symptoms = match_symptoms(stemmed_tokens, stemmed_dict)
    no_matched_symptoms(matched_symptoms)
    print(matched_symptoms)
    return matched_symptoms






