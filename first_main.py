import pandas as pd
import os
import re
from collections import defaultdict
import json

def process_excel_to_csv_and_dict(excel_file_path='zeit.xlsx'):
    """
    Process Excel file with multiple sheets to CSV files and create a unified dictionary.
    
    Args:
        excel_file_path (str): Path to the Excel file
    
    Returns:
        dict: Unified dictionary with date -> room -> student data structure
    """
    
    # Read all sheets from Excel file
    excel_data = pd.read_excel(excel_file_path, sheet_name=None, header=None)
    
    # Main dictionary to store all data
    unified_dict = {}
    
    # Process each sheet
    for sheet_name, df in excel_data.items():
        print(f"Processing sheet: {sheet_name}")
        
        # Convert DataFrame to list of lists for easier processing
        data = df.values.tolist()

        #print(data)
        
        # Extract date and process rooms
        date, room_data = extract_date_and_rooms(data)

        #print(f"Extracted date: {date}, room data found: {room_data} ")
        
        if date:
            unified_dict[date] = room_data
            
            # Create CSV files for each room
            create_csv_files(date, room_data)
    
    return unified_dict

def extract_date_and_rooms(data):
    """
    Extract date and room data from the sheet data.
    
    Args:
        data (list): List of rows from the sheet
    
    Returns:
        tuple: (date_string, room_dict)
    """
    
    date = None
    room_dict = {}
    current_room = None
    room_data = []
    
    for row in data:
        # Convert row to string to check for date and room headers
        row_str = str(row[0]) if row and len(row) > 0 and pd.notna(row[0]) else ""
        
        # Check for date header (e.g., "23.06.2023: Raum A")
        if ": Raum" in row_str:
            # Save previous room data if exists
            if current_room and room_data:
                room_dict[current_room] = process_room_data(room_data)
                room_data = []
            
            # Extract date and room
            parts = row_str.split(": Raum ")
            if len(parts) == 2:
                date = parts[0]
                current_room = f"Room {parts[1]}"
        
        # Check if it's a data row (has student ID pattern like DiA11, DiB21, etc.)
        #elif row and len(row) > 0 and pd.notna(row[0]) and re.match(r'Di[ABC]\d{2}', str(row[0])):
        elif row and len(row) > 0 and pd.notna(row[0]) and re.match(r'(Mo|Di|Mi|Do|Fr|Sa|So)[A-Z]\d{2}', str(row[0])):

            room_data.append(row)
    
    #print(room_data)
    # Don't forget the last room
    if current_room and room_data:
        room_dict[current_room] = process_room_data(room_data)
    
    return date, room_dict

def process_room_data(room_data):
    """
    Process room data into dictionary format.
    
    Args:
        room_data (list): List of rows for a specific room
    
    Returns:
        dict: Dictionary with student IDs as keys
    """
    
    room_dict = {}
    
    for row in room_data:
        if len(row) >= 15:  # Ensure we have enough columns
            student_id = str(row[0]) if pd.notna(row[0]) else ""
            
            if student_id:  # Only process rows with student IDs
                room_dict[student_id] = {
                    'Nachname': str(row[1]) if pd.notna(row[1]) else "",
                    'Vorname': str(row[2]) if pd.notna(row[2]) else "",
                    'Fach': str(row[3]) if pd.notna(row[3]) else "",
                    'Gäste': str(row[4]) if pd.notna(row[4]) else "",
                    'Prüfer*in': str(row[5]) if pd.notna(row[5]) else "",
                    'Protokoll': str(row[6]) if pd.notna(row[6]) else "",
                    'Vorsitz': str(row[7]) if pd.notna(row[7]) else "",
                    'Ankunft_in_Warteraum_1': str(row[8]) if pd.notna(row[8]) else "",
                    'Beginn_d_Vorbereitung': str(row[9]) if pd.notna(row[9]) else "",
                    'Ende_der_Vorbereitung': str(row[10]) if pd.notna(row[10]) else "",
                    'Beginn_Prüfung': str(row[11]) if pd.notna(row[11]) else "",
                    'Ende_Prüfung': str(row[12]) if pd.notna(row[12]) else "",
                    'Beratung_von': str(row[13]) if pd.notna(row[13]) else "",
                    'Beratung_bis': str(row[14]) if pd.notna(row[14]) else "",
                    'Aufsicht_Warteraum_1': str(row[15]) if len(row) > 15 and pd.notna(row[15]) else "",
                    'Aufsicht_Warteraum_2': str(row[16]) if len(row) > 16 and pd.notna(row[16]) else "",
                    'Aufsicht_Vorbereitungsraum': str(row[17]) if len(row) > 17 and pd.notna(row[17]) else "",
                    'Fluraufsicht': str(row[18]) if len(row) > 18 and pd.notna(row[18]) else "",
                    'Reserve': str(row[19]) if len(row) > 19 and pd.notna(row[19]) else ""
                }
    
    return room_dict

def create_csv_files(date, room_data):
    """
    Create CSV files for each room.
    
    Args:
        date (str): Date string
        room_data (dict): Dictionary containing room data
    """
    
    # Create directory if it doesn't exist
    os.makedirs('csv_output', exist_ok=True)
    
    for room_name, students in room_data.items():
        # Create filename
        room_letter = room_name.split()[-1]  # Get A, B, or C
        filename = f"csv_output/{date}_Room{room_letter}.csv"
        
        # Prepare data for CSV
        csv_data = []
        
        # Header row
        headers = ['Nr.', 'Nachname', 'Vorname', 'Fach', 'Gäste', 'Prüfer*in', 'Protokoll', 'Vorsitz',
                  'Ankunft in Warteraum 1', 'Beginn d. Vorbereitung', 'Ende der Vorbereitung',
                  'Beginn Prüfung', 'Ende Prüfung', 'Beratung von', 'Beratung bis',
                  'Aufsicht Warteraum 1', 'Aufsicht Warteraum 2', 'Aufsicht Vorbereitungsraum',
                  'Fluraufsicht', 'Reserve']
        
        csv_data.append(headers)
        
        # Add student data
        for student_id, student_info in students.items():
            row = [
                student_id,
                student_info['Nachname'],
                student_info['Vorname'],
                student_info['Fach'],
                student_info['Gäste'],
                student_info['Prüfer*in'],
                student_info['Protokoll'],
                student_info['Vorsitz'],
                student_info['Ankunft_in_Warteraum_1'],
                student_info['Beginn_d_Vorbereitung'],
                student_info['Ende_der_Vorbereitung'],
                student_info['Beginn_Prüfung'],
                student_info['Ende_Prüfung'],
                student_info['Beratung_von'],
                student_info['Beratung_bis'],
                student_info['Aufsicht_Warteraum_1'],
                student_info['Aufsicht_Warteraum_2'],
                student_info['Aufsicht_Vorbereitungsraum'],
                student_info['Fluraufsicht'],
                student_info['Reserve']
            ]
            csv_data.append(row)
        
        # Write to CSV
        df_csv = pd.DataFrame(csv_data)
        df_csv.to_csv(filename, index=False, header=False)
        print(f"Created CSV file: {filename}")



# # Main execution
# if __name__ == "__main__":
#     # Process Excel file
#     print("Processing Excel file...")
#     excel_dict = process_excel_to_csv_and_dict('zeit.xlsx')
    
#     # Process existing CSV file
#     print("\nProcessing existing CSV file...")
#     #csv_dict = process_existing_csv('zeit_final.csv')
    
#     # Combine dictionaries
#     unified_dict = { **excel_dict}
    

#     # Convert and save to JSON file
#     with open("zeit.json", "w") as f:
#         json.dump(unified_dict, f, indent=4)  # indent=4 makes it pretty-printed