import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import utils
import os

# Initialize session state
if 'current_date' not in st.session_state:
    st.session_state.current_date = datetime.now()

# Page configuration
st.set_page_config(
    page_title="Staff Roster Management",
    page_icon="📅",
    layout="wide"
)

# Initialize data files if they don't exist
if not os.path.exists('data'):
    os.makedirs('data')

if not os.path.exists('data/staff.csv'):
    pd.DataFrame(columns=['id', 'name', 'role']).to_csv('data/staff.csv', index=False)

if not os.path.exists('data/shifts.csv'):
    pd.DataFrame(columns=['date', 'staff_id', 'shift_type', 'location']).to_csv('data/shifts.csv', index=False)

def main():
    st.title("📅 Staff Roster Management")

    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Daily Schedule", "Staff Management"])

    if page == "Daily Schedule":
        show_daily_schedule()
    else:
        show_staff_management()

def show_daily_schedule():
    # Date navigation
    col1, col2, col3 = st.columns([1,3,1])
    with col1:
        if st.button("← Previous Day"):
            st.session_state.current_date -= timedelta(days=1)
    with col2:
        st.header(f"Schedule for {st.session_state.current_date.strftime('%B %d, %Y')}")
    with col3:
        if st.button("Next Day →"):
            st.session_state.current_date += timedelta(days=1)

    # Load data
    staff_df = pd.read_csv('data/staff.csv')
    shifts_df = pd.read_csv('data/shifts.csv')

    # Define locations in order
    locations = [
        "Reception desk 1",
        "Reception desk 2",
        "A-Team Office",
        "Morning Tea break",
        "Lunch",
        "Reception backup"
    ]

    # Get current date's shifts
    current_date_str = st.session_state.current_date.strftime('%Y-%m-%d')
    day_shifts = shifts_df[shifts_df['date'] == current_date_str]

    # Create schedule table
    schedule_data = []
    for location in locations:
        row = {'Location': location}
        for staff in staff_df.itertuples():
            shift = day_shifts[(day_shifts['staff_id'] == staff.id) & 
                             (day_shifts['location'] == location)]
            row[staff.name] = shift['shift_type'].iloc[0] if not shift.empty else ""
        schedule_data.append(row)

    # Display schedule
    schedule_df = pd.DataFrame(schedule_data)
    st.dataframe(schedule_df, use_container_width=True)

    # Add new shift
    st.subheader("Add Shift")
    with st.form("add_shift"):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            selected_staff = st.selectbox("Select Staff", 
                                        options=staff_df['name'].tolist(),
                                        key="staff_select")
        with col2:
            selected_date = st.date_input("Select Date", 
                                        value=st.session_state.current_date,
                                        key="date_select")
        with col3:
            shift_type = st.selectbox("Shift Type", 
                                    options=["Morning", "Afternoon", "Night"],
                                    key="shift_select")
        with col4:
            location = st.selectbox("Location",
                                  options=locations,
                                  key="location_select")

        if st.form_submit_button("Add Shift"):
            staff_id = staff_df[staff_df['name'] == selected_staff]['id'].iloc[0]
            if utils.add_shift(staff_id, selected_date, shift_type, location):
                st.success("Shift added successfully!")
                st.rerun()

    # Export button
    if st.button("Export Schedule"):
        utils.export_schedule([st.session_state.current_date])
        st.success("Schedule exported successfully!")

def show_staff_management():
    st.subheader("Staff Management")

    # Display current staff with edit functionality
    staff_df = pd.read_csv('data/staff.csv')

    # Create columns for each staff member's details
    for idx, staff in staff_df.iterrows():
        col1, col2, col3, col4 = st.columns([2, 2, 1, 1])
        with col1:
            st.write(f"**Name:** {staff['name']}")
        with col2:
            new_role = st.selectbox(
                "Role",
                options=["Manager", "Senior Staff", "Junior Staff", "Supported Employee", "Admin Assistant"],
                key=f"role_{staff['id']}",
                index=["Manager", "Senior Staff", "Junior Staff", "Supported Employee", "Admin Assistant"].index(staff['role'])
            )
        with col3:
            if st.button("Update Role", key=f"update_{staff['id']}"):
                utils.update_staff_role(staff['id'], new_role)
                st.success(f"Updated role for {staff['name']}")
                st.rerun()
        with col4:
            if st.button("🗑️ Remove", key=f"remove_{staff['id']}", type="secondary"):
                utils.remove_staff(staff['id'])
                st.success(f"Removed {staff['name']}")
                st.rerun()
        st.divider()

    # Add new staff
    st.subheader("Add New Staff")
    with st.form("add_staff"):
        col1, col2 = st.columns(2)
        with col1:
            new_name = st.text_input("Name")
        with col2:
            new_role = st.selectbox("Role", ["Manager", "Senior Staff", "Junior Staff", "Supported Employee", "Admin Assistant"])

        if st.form_submit_button("Add Staff"):
            utils.add_staff(new_name, new_role)
            st.success("Staff member added successfully!")
            st.rerun()

if __name__ == "__main__":
    main()