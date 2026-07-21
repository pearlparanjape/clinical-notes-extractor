import os
import streamlit as st
import pandas as pd
from src.claude_client import ClaudeClient
from src.extractor import extract_demographics, extract_symptoms, extract_blood_tests

if "ANTHROPIC_API_KEY" in st.secrets:
    os.environ["ANTHROPIC_API_KEY"] = st.secrets["ANTHROPIC_API_KEY"]

st.set_page_config(
    page_title="Clinical Notes Extractor",
    page_icon="📊",
    layout="wide",
)

st.title("Clinical Notes Extractor")
st.warning(
    "**⚠️ Demo only — do NOT enter real patient data or PHI.** "
    "This is a demonstration using synthetic clinical notes. "
    "Text entered is sent to a third-party LLM API and is not stored."
)
st.write(
    "Extract structured demographics, symptoms, and lab tests from free-text "
    "clinical notes using an LLM with schema validation."
)

note = st.text_area("Clinical note", height=200)

if st.button("Extract"):
    if not note.strip():
        st.warning("Please paste a clinical note first.")
    else:
        with st.spinner("Extracting structured data..."):
            client = ClaudeClient()

            # --- Demographics (single object) ---
            st.header("Demographics")
            demo = extract_demographics(note, client)
            if demo["status"] == "ok":
                st.dataframe(pd.DataFrame([demo["data"]]))
            else:
                st.error(f"Error: {demo['stage']}")

            # --- Symptoms (list) ---
            st.header("Symptoms")
            symp = extract_symptoms(note, client)
            if symp["status"] == "ok":
                if symp["data"]:
                    st.dataframe(pd.DataFrame(symp["data"]))
                else:
                    st.info("No symptoms found.")
            else:
                st.error(f"Error: {symp['stage']}")

            # --- Lab tests (list) ---
            st.header("Laboratory Tests")
            lab = extract_blood_tests(note, client)
            if lab["status"] == "ok":
                if lab["data"]:
                    st.dataframe(pd.DataFrame(lab["data"]))
                else:
                    st.info("No laboratory tests found.")
            else:
                st.error(f"Error: {lab['stage']}")