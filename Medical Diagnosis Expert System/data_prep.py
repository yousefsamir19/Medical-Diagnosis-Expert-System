import pandas as pd
import os

def load_data():
    
 df = pd.read_csv(os.path.join(os.path.dirname(__file__), "Medical Diagnosis Expert System.csv"))
 
 df.columns = df.columns.str.strip().str.lower()
 
 df = df.drop_duplicates()
 df = df.dropna()
 
 df["disease"] = df["disease"].str.strip().str.lower().str.replace(" ", "_")
 df["symptoms"] = df["symptoms"].str.strip().str.lower()
 df["precautions"] = df["precautions"].str.strip().str.lower()
 
 df["symptoms"] = df["symptoms"].apply(
    lambda x: [s.strip().replace(" ", "_") for s in x.split(",")])
 
 df["precautions"] = df["precautions"].apply(
    lambda x: [p.strip() for p in x.split(",")])
 
 all_symptoms = sorted(set(
    symptom
    for symptom_list in df["symptoms"]
    for symptom in symptom_list))
 
 knowledge = []
 for _, row in df.iterrows():
   i=0
   knowledge.append({
      "id": i,
      "name": row["disease"],
      "symptoms": row["symptoms"],
      "precautions": row["precautions"]
     })
   i+=1
     
 return knowledge, all_symptoms

patterns, all_symptoms = load_data()