import pandas as pd
import os

from src import config
from src.claude_client import ClaudeClient
from src.extractor import extract_demographics, extract_symptoms, extract_blood_tests


def load_notes(n: int) -> pd.DataFrame:
    print(f"Loading {n} notes from Hugging Face...")
    df = pd.read_json(config.DATASET, lines=True)  # config.DATASET
    return df.sample(n=n, random_state=config.RANDOM_STATE).reset_index(drop=True)


def extract_all(notes: pd.DataFrame, client: ClaudeClient):
    demo_results = []
    symptom_rows = []
    lab_test_rows = []

    for i, row in notes.iterrows():
        note_text = row[config.NOTE_COLUMN]

        # --- demographics (one object per note) ---
        demo = extract_demographics(note_text, client)
        if demo["status"] == "ok":
            demo_results.append({"note_id": i, **demo["data"]})
        else:
            demo_results.append({"note_id": i, "error_stage": demo["stage"]})
            print(
                f"  note {i}  ⚠️  DEMOGRAPHICS ERROR "
                f"({demo['stage']}): {demo['error']}"
            )

        # --- symptoms (a list per note) ---
        symp = extract_symptoms(note_text, client)
        if symp["status"] == "ok":
            for s in symp["data"]:
                symptom_rows.append({"note_id": i, **s})
        else:
            symptom_rows.append({"note_id": i, "error_stage": symp["stage"]})
            print(
                f"  note {i}  ⚠️  SYMPTOMS ERROR " f"({symp['stage']}): {symp['error']}"
            )

        # --- lab tests (a list per note) ---
        lab_tests = extract_blood_tests(note_text, client)
        if lab_tests["status"] == "ok":
            for lt in lab_tests["data"]:
                lab_test_rows.append({"note_id": i, **lt})
        else:
            lab_test_rows.append({"note_id": i, "error_stage": lab_tests["stage"]})
            print(
                f"  note {i}  ⚠️  LAB TESTS ERROR "
                f"({lab_tests['stage']}): {lab_tests['error']}"
            )

        print(f"  extracted {i + 1}/{len(notes)}")

    return (
        pd.DataFrame(demo_results),
        pd.DataFrame(symptom_rows),
        pd.DataFrame(lab_test_rows),
    )


def main():
    notes = load_notes(config.N_NOTES)
    client = ClaudeClient()
    demographics, symptoms, lab_tests = extract_all(notes, client)

    os.makedirs(config.OUTPUT_DIR, exist_ok=True)

    notes.to_csv(f"{config.OUTPUT_DIR}/original.csv", index=False)
    demographics.to_csv(f"{config.OUTPUT_DIR}/demographics.csv", index=False)
    symptoms.to_csv(f"{config.OUTPUT_DIR}/symptoms.csv", index=False)
    lab_tests.to_csv(f"{config.OUTPUT_DIR}/lab_tests.csv", index=False)

    # combined: each symptom row joined to its note's demographics (denormalized view)
    combined = symptoms.merge(demographics, on="note_id", how="left")
    combined.to_csv(f"{config.OUTPUT_DIR}/combined.csv", index=False)

    print(f"\nDone. Wrote 4 files to {config.OUTPUT_DIR}/")


if __name__ == "__main__":
    main()
