import json
from collections import defaultdict

def solve_exam_schedule(students_data, schedule_data):
    """
    Assigns students to exam slots based on a set of constraints.

    Args:
        students_data (dict): A dictionary mapping subjects to lists of student groups.
        schedule_data (dict): A dictionary representing the available exam schedule.

    Returns:
        dict: The schedule_data dictionary populated with student assignments.
    """
    # 1. --- Pre-processing ---

    # Create a map of student names to their subjects for easy lookup.
    student_to_subjects = defaultdict(list)
    for subject, groups in students_data.items():
        for group in groups:
            for student_name in group:
                student_to_subjects[student_name].append(subject)

    # Create a comprehensive, ordered list of all available slot groups.
    # This respects the "early as possible" rule by sorting by day, room, and time.
    available_slot_groups = []
    sorted_days = sorted(schedule_data.keys())
    for day in sorted_days:
        sorted_rooms = sorted(schedule_data[day].keys())
        for room in sorted_rooms:
            # Sort slots to ensure chronological order (e.g., DiA11, DiA12, ..., DiA21)
            slots_in_room = sorted(schedule_data[day][room].keys())
            # A "slot group" is a block of 3 exams.
            for i in range(0, len(slots_in_room), 3):
                group_keys = slots_in_room[i:i + 3]
                if len(group_keys) == 3:
                    available_slot_groups.append({
                        "day": day,
                        "room": room,
                        "slots": group_keys,
                        "used": False
                    })

    # --- Helper function to find and assign a subject ---
    def find_and_assign(subject, preferred_day=None):
        """Finds available slots and assigns a subject's groups to them."""
        nonlocal available_slot_groups
        groups_to_schedule = students_data[subject]
        slots_found = []

        # Find enough consecutive, available slot groups for the subject
        for slot_group in available_slot_groups:
            # Skip if already used
            if slot_group["used"]:
                continue
            # If a specific day is required, skip slots on other days
            if preferred_day and slot_group["day"] != preferred_day:
                continue

            slots_found.append(slot_group)
            if len(slots_found) == len(groups_to_schedule):
                break # Found enough slots
        
        # If not enough slots were found, reset and try without a day preference
        # This can happen if a day is full but other days are available.
        if len(slots_found) < len(groups_to_schedule):
             slots_found = []
             for slot_group in available_slot_groups:
                if not slot_group["used"]:
                    slots_found.append(slot_group)
                    if len(slots_found) == len(groups_to_schedule):
                        break


        if len(slots_found) < len(groups_to_schedule):
            print(f"!!! Warning: Could not find enough slots for {subject}")
            return None

        # Assign the groups to the found slots
        assigned_day = slots_found[0]["day"]
        for i, group_data in enumerate(groups_to_schedule):
            current_slot_info = slots_found[i]
            slot_keys = current_slot_info["slots"]
            for j, student_name in enumerate(group_data):
                slot_key = slot_keys[j]
                vorname, nachname = student_name.split(" ", 1)
                
                # Update the main schedule dictionary
                schedule_data[current_slot_info["day"]][current_slot_info["room"]][slot_key].update({
                    "Nachname": nachname,
                    "Vorname": vorname,
                    "Fach": subject
                })
            # Mark this slot group as used for the next search
            current_slot_info["used"] = True

        return assigned_day

    # 2. --- Main Scheduling Logic ---
    
    subjects_to_schedule = list(students_data.keys())
    scheduled_subjects = set()
    student_day_constraints = {}

    # Start with the fixed subjects
    fixed_subjects = {"Informatik": "24.06.2025", "Philosophie": "24.06.2025"}
    for subject, day in fixed_subjects.items():
        if subject in subjects_to_schedule:
            assigned_day = find_and_assign(subject, preferred_day=day)
            scheduled_subjects.add(subject)
            # Add constraints for all students taking this subject
            for group in students_data[subject]:
                for student in group:
                    student_day_constraints[student] = assigned_day

    # Iteratively schedule remaining subjects based on propagating constraints
    while len(scheduled_subjects) < len(subjects_to_schedule):
        subject_scheduled_this_iteration = False
        # First pass: try to schedule subjects that are now constrained
        for subject in subjects_to_schedule:
            if subject in scheduled_subjects:
                continue

            constrained_day = None
            for group in students_data[subject]:
                for student in group:
                    if student in student_day_constraints:
                        constrained_day = student_day_constraints[student]
                        break
                if constrained_day:
                    break
            
            if constrained_day:
                assigned_day = find_and_assign(subject, preferred_day=constrained_day)
                scheduled_subjects.add(subject)
                # Propagate constraints to other students in this subject
                for group in students_data[subject]:
                    for student in group:
                        student_day_constraints[student] = assigned_day
                subject_scheduled_this_iteration = True
                break # Restart the while loop to re-evaluate constraints

        # Second pass: if no subjects were scheduled due to constraints, schedule the next available one
        if not subject_scheduled_this_iteration:
            for subject in subjects_to_schedule:
                if subject not in scheduled_subjects:
                    assigned_day = find_and_assign(subject)
                    scheduled_subjects.add(subject)
                    # Add constraints for all students taking this subject
                    for group in students_data[subject]:
                        for student in group:
                            student_day_constraints[student] = assigned_day
                    break # Break to restart the while loop

    return schedule_data


if __name__ == '__main__':
    # Load the student and time data from the provided JSON files
    try:
        with open('student.json', 'r', encoding='utf-8') as f:
            students = json.load(f)
        with open('zeit.json', 'r', encoding='utf-8') as f:
            zeitplan = json.load(f)
    except FileNotFoundError:
        print("Make sure 'student.json' and 'zeit.json' are in the same directory.")
        exit()

    # Run the scheduling algorithm
    final_schedule = solve_exam_schedule(students, zeitplan)

    # Print the resulting schedule in a readable format
    output_file_name = "final_schedule.json"
    with open(output_file_name, 'w', encoding='utf-8') as f:
        json.dump(final_schedule, f, ensure_ascii=False, indent=4)
        
    print(f"Scheduling complete. The final schedule has been saved to '{output_file_name}'")

    # Optional: Print a summary to the console
    print("\n--- Scheduled Exam Summary ---")
    unassigned_students = []
    total_exams = sum(len(group) for subject in students for group in students[subject])
    scheduled_exams = 0

    for day, rooms in final_schedule.items():
        print(f"\n--- {day} ---")
        for room, slots in rooms.items():
            for slot_id, details in slots.items():
                if details.get("Fach"):
                    print(f"{room} - {slot_id}: {details['Vorname']} {details['Nachname']} - {details['Fach']}")
                    scheduled_exams += 1
    
    print(f"\nTotal exams to schedule: {total_exams}")
    print(f"Total exams scheduled: {scheduled_exams}")

    if total_exams != scheduled_exams:
        print("\n!!! WARNING: Not all students were scheduled. Please check the inputs and logic.")

