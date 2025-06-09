import json
import pandas as pd


def convert_to_csv(raw_data):
    # Load the JSON file
    # with open(final_json, "r", encoding="utf-8") as f:
    #     raw_data = json.load(f)

    # Flatten the nested structure
    rows = []

    for date, rooms in raw_data.items():
        for room, slots in rooms.items():
            for slot_id, exam in slots.items():
                row = {
                    "Date": date,
                    "Room": room,
                    "Slot": slot_id,
                    **exam  # unpack the inner exam dictionary
                }
                rows.append(row)

    # Convert to DataFrame
    df = pd.DataFrame(rows)

    return df

    #df.to_csv("exams_optimised_gemini.csv", index=False, encoding="utf-8-sig")