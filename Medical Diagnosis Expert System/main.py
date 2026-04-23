import data_prep as data
import Tokenization as tk
from ExpertSystem import MedicalExpertSystem, diseases_matched
from collections import Counter
from functools import reduce
from nltk import word_tokenize

patterns, all_symptoms = data.load_data()
already_asked = []

def load_stemmed_symptom_dict():
    stemmed_symptom_dict = {}
    for symptom in all_symptoms:
        words = symptom.replace("_", " ")
        words = tk.tokenizer.tokenize(words)
        words = [w for w in words if w not in tk.stop_words]

        stemmed_words = frozenset(tk.ps.stem(w) for w in words)
        stemmed_symptom_dict[stemmed_words] = symptom

    return stemmed_symptom_dict


stemmed_symptom_dict = load_stemmed_symptom_dict()
text = input("Describe your symptoms: ")
matched_symptoms = tk.extract_symptoms(text,stemmed_symptom_dict)


#res is the diseases with 0.50 or less cf
def ask_clarifying_questions(res, current_matched_symptoms):
    potential_symp=[]
    for disease in res:
        potential_symp.extend(disease['missed'])
    counts = Counter(potential_symp)
    # shared symptoms between diseases
    sorted_symp = list(counts)

    for symp in sorted_symp:
        if symp in already_asked:
            continue
        else:
            answer = input(f"Are you experiencing {symp}? (y/n): ").strip().lower()
            already_asked.append(symp)
            if answer == "y":
                current_matched_symptoms.append(symp)
                print(current_matched_symptoms)
                return True
    print(current_matched_symptoms)
    return False


if matched_symptoms:
    while True:
        engine = MedicalExpertSystem(matched_symptoms, patterns)
        engine.reset()
        engine.run()
        #sort according to the CF (descending)
        results = [dict(fact) for fact in engine.facts.values() if isinstance(fact, diseases_matched)]
        results.sort(key=lambda x: x['cf'], reverse=True)

        if results and results[0]['cf'] < 0.8:
            if not ask_clarifying_questions(results, matched_symptoms):
                break
        else:
            break




