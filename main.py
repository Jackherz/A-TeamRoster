import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import utils
import os

# Initialize session state
if 'current_week' not in st.session_state:
    st.session_state.current_week = datetime.now()

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
    pd.DataFrame(columns=['date', 'staff_id', 'shift_type']).to_csv('data/shifts.csv', index=False)

def main():
    st.title("📅 Staff Roster Management")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Weekly Schedule", "Staff Management"])
    
    if page == "Weekly Schedule":
        show_weekly_schedule()
    else:
        show_staff_management()

def show_weekly_schedule():
    # Week navigation
    col1, col2, col3 = st.columns([1,3,1])
    with col1:
        if st.button("← Previous Week"):
            st.session_state.current_week -= timedelta(days=7)
    with col2:
        st.header(f"Week of {st.session_state.current_week.strftime('%B %d, %Y')}")
    with col3:
        if st.button("Next Week →"):
            st.session_state.current_week += timedelta(days=7)

    # Get week dates
    week_dates = utils.get_week_dates(st.session_state.current_week)
    staff_df = pd.read_csv('data/staff.csv')
    shifts_df = pd.read_csv('data/shifts.csv')
    
    # Schedule display
    st.subheader("Weekly Schedule")
    
    # Create schedule table
    schedule_table = []
    for staff in staff_df.itertuples():
        row = [staff.name]
        for date in week_dates:
            date_str = date.strftime('%Y-%m-%d')
            shift = shifts_df[(shifts_df['staff_id'] == staff.id) & 
                            (shifts_df['date'] == date_str)]['shift_type'].values
            row.append(shift[0] if len(shift) > 0 else "")
        schedule_table.append(row)

    # Display schedule
    df_schedule = pd.DataFrame(
        schedule_table,
        columns=['Staff'] + [d.strftime('%a %m/%d') for d in week_dates]
    )
    st.dataframe(df_schedule, use_container_width=True)

    # Add new shift
    st.subheader("Add Shift")
    with st.form("add_shift"):
        col1, col2, col3 = st.columns(3)
        with col1:
            selected_staff = st.selectbox("Select Staff", 
                                        options=staff_df['name'].tolist(),
                                        key="staff_select")
        with col2:
            selected_date = st.date_input("Select Date", 
                                        value=st.session_state.current_week,
                                        key="date_select")
        with col3:
            shift_type = st.selectbox("Shift Type", 
                                    options=["Morning", "Afternoon", "Night"],
                                    key="shift_select")
        
        if st.form_submit_button("Add Shift"):
            staff_id = staff_df[staff_df['name'] == selected_staff]['id'].iloc[0]
            utils.add_shift(staff_id, selected_date, shift_type)
            st.success("Shift added successfully!")
            st.rerun()

    # Export button
    if st.button("Export Schedule"):
        utils.export_schedule(week_dates)
        st.success("Schedule exported successfully!")

def show_staff_management():
    st.subheader("Staff Management")
    
    # Display current staff
    staff_df = pd.read_csv('data/staff.csv')
    st.dataframe(staff_df[['name', 'role']], use_container_width=True)
    
    # Add new staff
    st.subheader("Add New Staff")
    with st.form("add_staff"):
        col1, col2 = st.columns(2)
        with col1:
            new_name = st.text_input("Name")
        with col2:
            new_role = st.selectbox("Role", ["Manager", "Senior Staff", "Junior Staff", "Supported Employee"])
        
        if st.form_submit_button("Add Staff"):
            utils.add_staff(new_name, new_role)
            st.success("Staff member added successfully!")
            st.rerun()

if __name__ == "__main__":
    main()