from experta import *

#task 2
#prepare the data


class diseases_symptom(Fact):
    pass


class diseases_matched(Fact):
    pass


class MedicalExpertSystem(KnowledgeEngine):
    def __init__(self, matched_symptoms, knowledge_base):
            super().__init__()
            self.matched_symptoms = matched_symptoms
            self.knowledge_base = knowledge_base

    @DefFacts()
    def _initial_action(self):
            # yield Fact(action="find_disease")
            for symptom in self.matched_symptoms:
                yield diseases_symptom(name=symptom)

    @Rule()
    def diagnose(self):
            for obj in self.knowledge_base:
            #i want to get the intersection with eah disease and if it is not empty,
            #add the matched as facts and missed symptomps also
                matched = set(obj["symptoms"]).intersection(set(self.matched_symptoms))
                if matched:
                    missed = set(obj["symptoms"]).difference(set(self.matched_symptoms))
                    certainty = len(matched) / (len(matched) + len(missed))
                    self.declare(diseases_matched(id=obj["id"],
                                                  name=obj["name"],
                                                  matched=list(matched),
                                                  missed=list(missed),
                                                  counter=len(matched),
                                                  cf=certainty
                                                  ))

