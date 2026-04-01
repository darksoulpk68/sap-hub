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

    # Move the navigation to the sidebar to keep the workspace clean
    with st.sidebar:
        st.title(f"🏢 {department}")
        if st.button("⬅️ Change Department", use_container_width=True):
            del st.session_state.department
            st.rerun()

    st.title(f"{department} Transactions")

    if department == "Packaging":
        # Tabs act as "transaction separators"
        tab_oc1, tab_placeholder1, tab_placeholder2 = st.tabs(["OC1 - Material Order", "Onglet B", "Onglet C"])

        with tab_oc1:
            st.subheader("Transaction OC1: Material Requirements (LP12 Simulation)")
            st.write("Order materials or non-consumables for your packaging line.")

            # 1. Assign production line
            prod_line = st.selectbox("Select Production Line", ["Line 1", "Line 2", "Line 3", "Line 4"])

            # 2. Choose Material Source/Type
            mat_type = st.radio("Material Source", ["BOM Material (COR3 List)", "Non-consumable"])

            # 3. Dynamic selection based on the chosen material type
            if mat_type == "BOM Material (COR3 List)":
                material = st.selectbox("Select Material", ["MAT-1001 (Vials)", "MAT-1002 (Caps)", "MAT-1003 (Labels)"])
            else:
                material = st.selectbox("Select Non-consumable", ["Cellophane Roll", "Packaging Tape", "Glue Box"])

            # 4. Quantity selection
            quantity = st.number_input("Quantity", min_value=1, step=1)

            # 5. Create Transfer Order (TO)
            if st.button("Create TO (Transfer Order)", type="primary"):
                st.success(f"✅ Transfer Order created successfully!")
                st.info(f"**Action Executed:** {quantity}x {material} requested for {prod_line}. Pallet redirection processed via MSSR (PAD).")

    elif department == "Warehousing":
        st.info("Warehousing transactions are currently under construction.")
    elif department == "Manufacturing":
        st.info("Manufacturing transactions are currently under construction.")
    elif department == "Management":
        st.info("Management transactions are currently under construction.")
