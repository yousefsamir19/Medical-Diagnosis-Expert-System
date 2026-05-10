import streamlit as st
import collections
import collections.abc
collections.Mapping = collections.abc.Mapping

from collections import Counter
from nltk.stem import PorterStemmer
from nltk.tokenize import RegexpTokenizer
from nltk.corpus import stopwords
import nltk
import os, sys

sys.path.insert(0, os.path.dirname(__file__))

import data_prep as data
from ExpertSystem import MedicalExpertSystem, diseases_matched

nltk.download("stopwords", quiet=True)

# ── NLP setup ─────────────────────────────────────────────────────────────────
ps         = PorterStemmer()
stop_words = set(stopwords.words("english"))
tokenizer  = RegexpTokenizer(r"\w+")

# ── load knowledge base once ──────────────────────────────────────────────────
@st.cache_resource
def load_knowledge():
    patterns, all_symptoms = data.load_data()
    stemmed_dict = {}
    for symptom in all_symptoms:
        words       = symptom.replace("_", " ")
        words       = tokenizer.tokenize(words)
        words       = [w for w in words if w not in stop_words]
        stemmed_key = frozenset(ps.stem(w) for w in words)
        stemmed_dict[stemmed_key] = symptom
    return patterns, all_symptoms, stemmed_dict

patterns, all_symptoms, stemmed_dict = load_knowledge()

# ── NLP helpers ───────────────────────────────────────────────────────────────
def extract_symptoms(text):
    tokens   = tokenizer.tokenize(text.lower())
    filtered = [w for w in tokens if w not in stop_words]
    stemmed  = [ps.stem(w) for w in filtered]
    matched  = []
    for key, sym in stemmed_dict.items():
        if key.issubset(stemmed):
            matched.append(sym)
    return matched

def run_engine(matched_symptoms):
    engine = MedicalExpertSystem(matched_symptoms, patterns)
    engine.reset()
    engine.run()
    results = [dict(f) for f in engine.facts.values() if isinstance(f, diseases_matched)]

    # collapse duplicates — keep highest CF per disease name
    best = {}
    for disease in results:
        name = disease["name"]
        if name not in best or disease["cf"] > best[name]["cf"]:
            best[name] = disease
    results = sorted(best.values(), key=lambda x: x["cf"], reverse=True)

    return results

def get_clarifying_questions(results, already_asked):
    potential = []
    for d in results:
        potential.extend(d["missed"])
    counts = Counter(potential)
    return [s for s, _ in counts.most_common() if s not in already_asked]

def format_results(results):
    if not results:
        return "I couldn't determine a diagnosis. Please describe your symptoms in more detail."

    precautions_lookup = {e["name"]: e["precautions"] for e in patterns}

    top   = results[0]
    lines = ["### 🩺 Diagnosis Results\n"]
    lines.append("| Disease | Confidence |")
    lines.append("|---------|-----------|")
    for r in results[:5]:
        name = r["name"].replace("_", " ").title()
        pct  = round(r["cf"] * 100, 1)
        bar  = "🟩" * int(pct // 20) + "⬜" * (5 - int(pct // 20))
        lines.append(f"| {name} | {bar} {pct}% |")

    top_name = top["name"].replace("_", " ").title()
    lines.append(f"\n---\n### 💊 Precautions for **{top_name}**")
    precs = precautions_lookup.get(top["name"], [])
    if precs:
        for i, p in enumerate(precs, 1):
            lines.append(f"{i}. {p.capitalize()}")
    else:
        lines.append("No precautions found. Please consult a doctor.")

    return "\n".join(lines)

# ── page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Medical Diagnosis Assistant",
    page_icon="🏥",
    layout="centered"
)

# ── custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
body, .stApp { background: #0f1117; color: #e8eaf0; }

.header-box {
    background: linear-gradient(135deg, #1a237e 0%, #0d47a1 50%, #01579b 100%);
    border-radius: 16px;
    padding: 24px 32px;
    margin-bottom: 24px;
    text-align: center;
    box-shadow: 0 4px 24px rgba(13,71,161,0.4);
}
.header-box h1 { margin: 0; font-size: 1.8rem; color: #fff; }
.header-box p  { margin: 6px 0 0; color: #90caf9; font-size: 0.95rem; }

.chat-wrap { display: flex; flex-direction: column; gap: 12px; margin-bottom: 16px; }

.msg-user {
    align-self: flex-end;
    background: linear-gradient(135deg, #1565c0, #0d47a1);
    color: #fff;
    border-radius: 18px 18px 4px 18px;
    padding: 12px 18px;
    max-width: 75%;
    box-shadow: 0 2px 8px rgba(21,101,192,0.35);
    font-size: 0.95rem;
}
.msg-bot {
    align-self: flex-start;
    background: #1e2130;
    color: #e8eaf0;
    border-radius: 18px 18px 18px 4px;
    padding: 12px 18px;
    max-width: 85%;
    border: 1px solid #2a3050;
    box-shadow: 0 2px 8px rgba(0,0,0,0.3);
    font-size: 0.95rem;
}
.msg-label {
    font-size: 0.72rem;
    opacity: 0.55;
    margin-bottom: 4px;
    font-weight: 600;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}

.stTextInput > div > div > input {
    background: #1e2130 !important;
    border: 1.5px solid #2a3050 !important;
    border-radius: 12px !important;
    color: #e8eaf0 !important;
    padding: 12px 16px !important;
    font-size: 0.95rem !important;
}
.stTextInput > div > div > input:focus {
    border-color: #1565c0 !important;
    box-shadow: 0 0 0 3px rgba(21,101,192,0.2) !important;
}
.stButton > button {
    background: linear-gradient(135deg, #1565c0, #0d47a1) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 12px 28px !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    transition: opacity 0.2s !important;
}
.stButton > button:hover { opacity: 0.85 !important; }

.chip-row { display: flex; flex-wrap: wrap; gap: 8px; margin: 8px 0 16px; }
.chip {
    background: #1e2130;
    border: 1px solid #2a3050;
    border-radius: 20px;
    padding: 5px 14px;
    font-size: 0.8rem;
    color: #90caf9;
    cursor: default;
}

.disclaimer {
    background: #1a1f2e;
    border-left: 3px solid #f57f17;
    border-radius: 0 8px 8px 0;
    padding: 10px 16px;
    font-size: 0.8rem;
    color: #ffa726;
    margin-top: 16px;
}
</style>
""", unsafe_allow_html=True)

# ── header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="header-box">
  <h1>🏥 Medical Diagnosis Assistant</h1>
  <p>Describe your symptoms and I'll help identify possible conditions</p>
</div>
""", unsafe_allow_html=True)

# ── session state ─────────────────────────────────────────────────────────────
if "messages"         not in st.session_state: st.session_state.messages         = []
if "matched_symptoms" not in st.session_state: st.session_state.matched_symptoms = []
if "already_asked"    not in st.session_state: st.session_state.already_asked    = []
if "pending_qs"       not in st.session_state: st.session_state.pending_qs       = []
if "state"            not in st.session_state: st.session_state.state            = "init"
if "input_key"        not in st.session_state: st.session_state.input_key        = 0
# state: init | clarifying | done
# input_key: incremented after each send to reset the text input widget

# ── render chat history ───────────────────────────────────────────────────────
st.markdown('<div class="chat-wrap">', unsafe_allow_html=True)
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"""
        <div class="msg-user">
          <div class="msg-label">You</div>
          {msg["content"]}
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="msg-bot">
          <div class="msg-label">🤖 Assistant</div>
          {msg["content"]}
        </div>""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ── example chips (only at start) ────────────────────────────────────────────
if st.session_state.state == "init" and not st.session_state.messages:
    st.markdown("""
    <div>
      <div style="font-size:0.82rem;color:#607d8b;margin-bottom:6px;">💡 Try describing symptoms like:</div>
      <div class="chip-row">
        <span class="chip">I have chest pain and sweating</span>
        <span class="chip">itching and skin rash</span>
        <span class="chip">fever, headache and vomiting</span>
        <span class="chip">fatigue and weight loss</span>
      </div>
    </div>
    """, unsafe_allow_html=True)

# ── input row ─────────────────────────────────────────────────────────────────
placeholder = (
    "Start a new diagnosis by describing symptoms..."
    if st.session_state.state == "done"
    else "Describe your symptoms here..."
)

col1, col2 = st.columns([5, 1])
with col1:
    # changing key forces Streamlit to remount the widget — effectively clears it
    user_input = st.text_input(
        label="user_input",
        placeholder=placeholder,
        label_visibility="collapsed",
        key=f"input_box_{st.session_state.input_key}"
    )
with col2:
    send = st.button("Send")

# ── reset button ──────────────────────────────────────────────────────────────
if st.session_state.messages:
    if st.button("🔄 New Diagnosis"):
        for key in ["messages", "matched_symptoms", "already_asked", "pending_qs", "state"]:
            del st.session_state[key]
        st.session_state.input_key += 1
        st.rerun()

# ── process input ─────────────────────────────────────────────────────────────
if send and user_input.strip():
    user_text = user_input.strip()
    st.session_state.messages.append({"role": "user", "content": user_text})

    # ── INIT: extract symptoms from free text ──────────────────────────────
    if st.session_state.state in ("init", "done"):
        st.session_state.matched_symptoms = []
        st.session_state.already_asked    = []
        st.session_state.pending_qs       = []

        matched = extract_symptoms(user_text)
        st.session_state.matched_symptoms = matched

        if not matched:
            bot_reply = (
                "😕 I couldn't recognize any symptoms from your description.<br>"
                "Please try to be more specific.<br>"
                "<em>Example: 'I have itching, skin rash and fever'</em>"
            )
            st.session_state.messages.append({"role": "bot", "content": bot_reply})
            st.session_state.state = "init"
        else:
            symp_list = ", ".join(s.replace("_", " ") for s in matched)
            results   = run_engine(matched)

            if results and results[0]["cf"] >= 0.8:
                bot_reply  = f"✅ Recognized symptoms: <strong>{symp_list}</strong><br><br>"
                bot_reply += format_results(results).replace("\n", "<br>")
                st.session_state.messages.append({"role": "bot", "content": bot_reply})
                st.session_state.state = "done"
            else:
                qs = get_clarifying_questions(results, st.session_state.already_asked)
                st.session_state.pending_qs = qs
                st.session_state.state      = "clarifying"

                if qs:
                    next_q    = qs[0]
                    bot_reply = (
                        f"✅ Recognized symptoms: <strong>{symp_list}</strong><br><br>"
                        f"I need a bit more information to be confident.<br>"
                        f"Are you experiencing <strong>{next_q.replace('_', ' ')}</strong>? (yes / no)"
                    )
                    st.session_state.already_asked.append(next_q)
                else:
                    # no questions available → show best result now
                    bot_reply  = f"✅ Recognized symptoms: <strong>{symp_list}</strong><br><br>"
                    bot_reply += format_results(results).replace("\n", "<br>")
                    st.session_state.state = "done"

                st.session_state.messages.append({"role": "bot", "content": bot_reply})

    # ── CLARIFYING: handle yes/no answer ──────────────────────────────────
    elif st.session_state.state == "clarifying":
        answer = user_text.lower().strip()

        # if user said yes, add the last asked symptom to matched list
        if answer in ("yes", "y", "yeah", "yep", "sure", "yup"):
            last_q = st.session_state.already_asked[-1]
            st.session_state.matched_symptoms.append(last_q)

        # re-run engine with updated symptoms
        results = run_engine(st.session_state.matched_symptoms)

        if results and results[0]["cf"] >= 0.8:
            # confident enough — always show results after loop
            bot_reply = format_results(results).replace("\n", "<br>")
            st.session_state.messages.append({"role": "bot", "content": bot_reply})
            st.session_state.state = "done"
        else:
            qs = get_clarifying_questions(results, st.session_state.already_asked)
            st.session_state.pending_qs = qs

            if qs:
                next_q = qs[0]
                st.session_state.already_asked.append(next_q)
                bot_reply = (
                    f"Are you also experiencing "
                    f"<strong>{next_q.replace('_', ' ')}</strong>? (yes / no)"
                )
                st.session_state.messages.append({"role": "bot", "content": bot_reply})
            else:
                # no more questions — always show results after loop exits
                bot_reply = format_results(results).replace("\n", "<br>")
                st.session_state.messages.append({"role": "bot", "content": bot_reply})
                st.session_state.state = "done"

    # increment key to reset (clear) the text input widget
    st.session_state.input_key += 1
    st.rerun()

# ── disclaimer ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="disclaimer">
  ⚠️ <strong>Disclaimer:</strong> This tool is for educational purposes only and does not
  replace professional medical advice. Always consult a qualified healthcare provider.
</div>
""", unsafe_allow_html=True)