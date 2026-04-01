import streamlit as st

st.set_page_config(layout="wide")

# Check if a department has been selected in the session state
if 'department' not in st.session_state:
    st.title("SAP RBP Mock")
    st.header("Welcome to the SAP Mock Application")
    st.write(
        "This application simulates a Role-Based Permissions system. "
        "Please select your department to proceed."
    )

    st.divider()

    st.subheader("Department Selection")

    # Create columns for the menu buttons to create a full-size menu feel
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("📦 Packaging", use_container_width=True):
            st.session_state.department = "Packaging"
            st.rerun()

    with col2:
        if st.button("🏢 Warehousing", use_container_width=True):
            st.session_state.department = "Warehousing"
            st.rerun()

    with col3:
        if st.button("🔧 Manufacturing", use_container_width=True):
            st.session_state.department = "Manufacturing"
            st.rerun()

    with col4:
        if st.button("👔 Management", use_container_width=True):
            st.session_state.department = "Management"
            st.rerun()
else:
    # This part is displayed after a department is selected
    department = st.session_state.department
    st.title(f"Department: {department}")
    st.success(f"You have selected the **{department}** department.")
    st.info("In a real application, this would navigate you to the department-specific dashboard with appropriate permissions.")

    if st.button("⬅️ Go back to department selection"):
        del st.session_state.department
        st.rerun()
