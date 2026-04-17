import data_prep as data
from functools import reduce
from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import RegexpTokenizer
from experta import *

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
    return matched_symptoms
    
text = input("Describe your symptoms: ")
matched_symptoms = extract_symptoms(text)




#task 2

#prepare the data
from experta import *

# def matched_diseases():
class diseases_symptom(Fact):
    pass
class diseases_matched(Fact):
    pass
class MedicalExpertSystem(KnowledgeEngine):
    def __init__(self,matched_symptoms,patterns):
        super().__init__()
        self.matched_symptoms = matched_symptoms
        self.knowledge_base = patterns
    @DefFacts()
    def _initial_action(self):
        # yield Fact(action="find_disease")
        for symptom in self.matched_symptoms:
            yield diseases_symptom(name=symptom)
    @Rule()
    def diagonise(self):
        for obj in self.knowledge_base:
            #i want to get the intersection with eah disease and if it is not empty, add the matched as facts and missed symptomps also 
            matched = set(obj["symptoms"]).intersection(set(self.matched_symptoms))
            if matched:
                missed = set(obj["symptoms"]).difference(set(self.matched_symptoms))
                self.declare(diseases_matched(id=obj["id"], 
                                            name=obj["name"],
                                            matched=list(matched),
                                            missed=list(missed),
                                            counter=len(matched),
                                            ))


engine = MedicalExpertSystem(matched_symptoms,patterns)
engine.reset()    
engine.run()         
#i want to print   dieases_matched that is knowledge base
results_for_logic_lead = []

for fact in engine.facts.values():
    if isinstance(fact, diseases_matched):
        if fact['counter']/len(fact['matched'] + fact['missed']) >= 0.2:  # Only include diseases with at least 50% symptom match
           results_for_logic_lead.append(dict(fact))

for res in results_for_logic_lead:
    print(res)    
len(results_for_logic_lead)