import pandas as pd
from datetime import datetime, timedelta
import streamlit as st

def get_week_dates(date):
    """Return list of dates for the week containing the given date."""
    start = date - timedelta(days=date.weekday())
    return [start + timedelta(days=i) for i in range(7)]

def add_staff(name, role):
    """Add a new staff member to the staff.csv file."""
    staff_df = pd.read_csv('data/staff.csv')
    new_id = len(staff_df) + 1
    new_staff = pd.DataFrame([{
        'id': new_id,
        'name': name,
        'role': role
    }])
    staff_df = pd.concat([staff_df, new_staff], ignore_index=True)
    staff_df.to_csv('data/staff.csv', index=False)

def update_staff_role(staff_id, new_role):
    """Update the role of an existing staff member."""
    staff_df = pd.read_csv('data/staff.csv')
    staff_df.loc[staff_df['id'] == staff_id, 'role'] = new_role
    staff_df.to_csv('data/staff.csv', index=False)

def remove_staff(staff_id):
    """Remove a staff member and their associated shifts."""
    # Remove from staff.csv
    staff_df = pd.read_csv('data/staff.csv')
    staff_df = staff_df[staff_df['id'] != staff_id]
    staff_df.to_csv('data/staff.csv', index=False)

    # Remove associated shifts
    shifts_df = pd.read_csv('data/shifts.csv')
    shifts_df = shifts_df[shifts_df['staff_id'] != staff_id]
    shifts_df.to_csv('data/shifts.csv', index=False)

def add_shift(staff_id, date, shift_type, location):
    """Add a new shift to the shifts.csv file."""
    shifts_df = pd.read_csv('data/shifts.csv')

    # Check for conflicts
    date_str = date.strftime('%Y-%m-%d')
    
    # Check for time conflicts
    staff_shifts = shifts_df[
        (shifts_df['staff_id'] == staff_id) & 
        (shifts_df['date'] == date_str)
    ]
    
    if not staff_shifts.empty:
        new_start = datetime.strptime(shift_type.split('-')[0], '%H:%M').time()
        new_end = datetime.strptime(shift_type.split('-')[1], '%H:%M').time()
        
        for _, existing_shift in staff_shifts.iterrows():
            existing_start = datetime.strptime(existing_shift['shift_type'].split('-')[0], '%H:%M').time()
            existing_end = datetime.strptime(existing_shift['shift_type'].split('-')[1], '%H:%M').time()
            
            if (new_start < existing_end and new_end > existing_start):
                st.error("This staff member already has a shift that overlaps with this time slot!")
                return False
        
    # Check if location is already occupied
    location_shifts = shifts_df[
        (shifts_df['date'] == date_str) & 
        (shifts_df['location'] == location) &
        (shifts_df['shift_type'] == shift_type)
    ]
    if not location_shifts.empty:
        st.error("This location is already assigned to another staff member for this time slot!")
        return False

    # Get correct staff ID from name
    staff_df = pd.read_csv('data/staff.csv')
    correct_staff_id = staff_df[staff_df['id'] == staff_id]['id'].iloc[0]
    
    # Add new shift
    new_shift = pd.DataFrame([{
        'date': date_str,
        'staff_id': correct_staff_id,
        'shift_type': shift_type,
        'location': location
    }])
    shifts_df = pd.concat([shifts_df, new_shift], ignore_index=True)
    shifts_df.to_csv('data/shifts.csv', index=False)
    return True

def export_schedule(week_dates):
    """Export the schedule for the given week to a CSV file."""
    staff_df = pd.read_csv('data/staff.csv')
    shifts_df = pd.read_csv('data/shifts.csv')

    # Create export dataframe
    export_data = []
    for staff in staff_df.itertuples():
        row = {'Staff Name': staff.name, 'Role': staff.role}
        for date in week_dates:
            date_str = date.strftime('%Y-%m-%d')
            shift = shifts_df[(shifts_df['staff_id'] == staff.id) & 
                            (shifts_df['date'] == date_str)]
            if not shift.empty:
                row[date_str] = f"{shift['shift_type'].iloc[0]} ({shift['location'].iloc[0]})"
            else:
                row[date_str] = "Off"
        export_data.append(row)

    export_df = pd.DataFrame(export_data)
    export_filename = f"schedule_export_{week_dates[0].strftime('%Y%m%d')}.csv"
    export_df.to_csv(export_filename, index=False)
def remove_shift(staff_id, date, location):
    """Remove a shift for a specific staff member on a specific date and location."""
    shifts_df = pd.read_csv('data/shifts.csv')
    shifts_df = shifts_df[~((shifts_df['staff_id'] == staff_id) & 
                           (shifts_df['date'] == date) &
                           (shifts_df['location'] == location))]
    shifts_df.to_csv('data/shifts.csv', index=False)

def copy_day_shifts(source_date, target_date):
    """Copy all shifts from source date to target date."""
    shifts_df = pd.read_csv('data/shifts.csv')
    source_date_str = source_date.strftime('%Y-%m-%d')
    target_date_str = target_date.strftime('%Y-%m-%d')
    
    # Get shifts for source date
    source_shifts = shifts_df[shifts_df['date'] == source_date_str].copy()
    
    if not source_shifts.empty:
        # Update the date for the new shifts
        source_shifts['date'] = target_date_str
        
        # Remove any existing shifts in the target date
        shifts_df = shifts_df[shifts_df['date'] != target_date_str]
        
        # Add the copied shifts
        shifts_df = pd.concat([shifts_df, source_shifts], ignore_index=True)
        shifts_df.to_csv('data/shifts.csv', index=False)
        return True
    return False
