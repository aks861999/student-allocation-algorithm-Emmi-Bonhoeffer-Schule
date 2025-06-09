import streamlit as st
import pandas as pd
import io
import json

from first_main import process_excel_to_csv_and_dict
from second_assign import solve_exam_schedule
from third_convert_to_csv import convert_to_csv

# --- Streamlit Page Configuration ---
st.set_page_config(
    page_title="Student Allocation Algorithm Emmi Bonhoeffer Schule",
    page_icon="📊",
    layout="centered",
    initial_sidebar_state="expanded"
)

st.title("📊 Student Allocation Algorithm Emmi Bonhoeffer Schule")
st.write("Upload your Excel file and an optional JSON file, process them, and download the results as a CSV.")

# --- File Upload Section ---
st.header("Upload Files")

uploaded_excel_file = st.file_uploader("Choose an Excel file", type=["xlsx", "xls"])
uploaded_json_file = st.file_uploader("Choose a JSON file (Optional)", type=["json"])

# Variables to store loaded data
df = None
json_data = None

if uploaded_excel_file is not None:
    try:
        # Read the uploaded Excel file into a Pandas DataFrame
        df = pd.read_excel(uploaded_excel_file)
        st.success("Excel file uploaded successfully!")
        st.write("First 5 rows of the uploaded Excel data:")
        #st.dataframe(df.head())





    except Exception as e:
        st.error(f"Error reading Excel file: {e}")
        st.info("Please ensure you are uploading a valid Excel file.")

if df is not None and uploaded_json_file is not None:
    try:
        # Read the uploaded JSON file
        json_bytes = uploaded_json_file.read()
        json_string = json_bytes.decode('utf-8') # Decode bytes to string
        json_data = json.loads(json_string)
        st.success("JSON file uploaded successfully!")
        st.write("Content of the uploaded JSON file:")
        #st.json(json_data) # Display JSON data nicely
    except json.JSONDecodeError as e:
        st.error(f"Error decoding JSON file: {e}")
        st.info("Please ensure the uploaded file is a valid JSON format.")
    except Exception as e:
        st.error(f"An unexpected error occurred reading JSON file: {e}")

    st.subheader("Processing your data...")

    # Placeholder for your processing logic
    # Your processing logic will now likely take both 'df' and 'json_data' as inputs.
    
    # Example of your processing logic:
    # Assuming your processing logic takes the DataFrame 'df' and 'json_data' as inputs
    # and returns a processed DataFrame 'processed_df'

    processed_df = df.copy() # Start with a copy of the original DataFrame

    first_step = process_excel_to_csv_and_dict(uploaded_excel_file)

    second_step = solve_exam_schedule(json_data,first_step)

    processed_df = convert_to_csv(second_step)


    st.success("Data processing completed!")
    st.write("First 5 rows of the processed data:")
    st.dataframe(processed_df.head())

    # --- Download Section ---
    st.subheader("Download Processed Data")

    # Convert the processed DataFrame to CSV
    csv_buffer = io.StringIO()
    processed_df.to_csv(csv_buffer, index=False)
    csv_data = csv_buffer.getvalue()

    st.download_button(
        label="Download Processed CSV",
        data=csv_data,
        file_name="processed_data.csv",
        mime="text/csv"
    )
else:
    st.info("Please upload an Excel file to get started.")

st.sidebar.header("About")
st.sidebar.info(
    "This is a project to allocate students according to the availability of students and teachers for respective subjects for a final oral exam, Made with ❤️ by Akash"
)