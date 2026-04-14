import data_prep as data
from functools import reduce
from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import RegexpTokenizer
ps = PorterStemmer()
stop_words = set(stopwords.words('english'))
tokenizer = RegexpTokenizer(r'\w+')

patterns, all_symptoms = data.load_data()

def load_stemmed_symptom_dict():
    
    stemmed_symptom_dict = {}
    for symptom in all_symptoms:

        words = symptom.replace("_", " ")
        words = tokenizer.tokenize(words)
        words = [w for w in words if w not in stop_words]

        stemmed_words = frozenset(ps.stem(w) for w in words)
        stemmed_symptom_dict[stemmed_words] = symptom
    
    return stemmed_symptom_dict

stemmed_symptom_dict = load_stemmed_symptom_dict()

def process_user_input(user_input):
    
    tokens = tokenizer.tokenize(user_input)
    filtered_tokens = [word for word in tokens if word not in stop_words]
    
    stemmed_tokens = []
    for w in filtered_tokens:
        w = w.replace("_"," ")
        w = ps.stem(w)
        stemmed_tokens.append(w)
    
    return stemmed_tokens

def match_symptoms(stemmed_tokens):
    matched_symptoms = []
    for stemmed_key, original_symptom in stemmed_symptom_dict.items():
        if stemmed_key.issubset(stemmed_tokens):
            matched_symptoms.append(original_symptom)
    return matched_symptoms

def no_matched_symptoms(matched_symptoms):
    if len(matched_symptoms) == 0:
        print("\nSorry, I could not recognize any symptoms from what you described.")
        print("Please try to describe your symptoms more clearly.")
        print("Example: 'I have itching, skin rash and fever'")
    return True 

def extract_symptoms(user_input):
    stemmed_tokens = process_user_input(user_input)
    matched_symptoms = match_symptoms(stemmed_tokens)
    no_matched_symptoms(matched_symptoms)
    print(matched_symptoms)
    
text = input("Describe your symptoms: ")
extract_symptoms(text)
