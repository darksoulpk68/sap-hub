import streamlit as st
import pandas as pd
import numpy as np
import os
import google.generativeai as genai

st.set_page_config(layout="wide")

# --- GEMINI CHATBOT FUNCTIONALITY ---
@st.cache_data
def get_persona():
    """Loads the persona from the markdown file."""
    try:
        with open("./.gemini/persona.md", "r") as f:
            return f.read()
    except FileNotFoundError:
        return "You are a helpful assistant."

def sap_genius_chat():
    """The main function for the SAP Genius chatbot interface."""
    st.title("🧠 SAP Genius")
    st.write("Your personal SAP expert, powered by Gemini. Ask me anything about SAP processes, transactions, or ABAP logic, and I'll explain it in Python!")

    # --- API Key Management ---
    if 'gemini_api_key' not in st.session_state:
        st.session_state.gemini_api_key = os.environ.get("GEMINI_API_KEY", "")

    api_key_input = st.text_input(
        "Enter your Gemini API Key:",
        value=st.session_state.gemini_api_key,
        type="password",
        help="You can get your key from https://aistudio.google.com/app/apikey"
    )

    if api_key_input:
        st.session_state.gemini_api_key = api_key_input

    if not st.session_state.gemini_api_key:
        st.warning("Please enter your Gemini API Key to continue.")
        st.stop()

    try:
        genai.configure(api_key=st.session_state.gemini_api_key)
        model = genai.GenerativeModel(
            model_name="gemini-1.5-pro-latest",
            system_instruction=get_persona()
        )
    except Exception as e:
        st.error(f"Error configuring Gemini: {e}")
        st.stop()


    # --- Chat History Management ---
    if "chat" not in st.session_state:
        st.session_state.chat = model.start_chat(history=[])

    # Display chat messages
    for message in st.session_state.chat.history:
        role = "assistant" if message.role == "model" else message.role
        with st.chat_message(role):
            st.markdown(message.parts[0].text)

    # --- User Input ---
    if prompt := st.chat_input("Ask SAP Genius..."):
        with st.chat_message("user"):
            st.markdown(prompt)

        try:
            with st.spinner("🧠 Genius is thinking..."):
                response = st.session_state.chat.send_message(prompt)
            with st.chat_message("assistant"):
                st.markdown(response.text)
        except Exception as e:
            st.error(f"An error occurred: {e}")

# --- MOCK PERMISSIONS MATRIX ---
# This matrix tells your IT team exactly what granular authorization checks they need to build.
ROLE_PERMISSIONS = {
    "Packaging": ["VIEW_OC1", "CREATE_PACKAGING_TO"],
    "Warehousing": ["VIEW_OE1", "VIEW_OE2", "CONFIRM_PICK_TO", "ORDER_MFG_BATCH", "VIEW_STAGING"],
    "Manufacturing": ["VIEW_MFG_DASHBOARD", "CONFIRM_PROCESS_ORDER"],
    "Management": ["VIEW_ALL_REPORTS", "APPROVE_VARIANCES"]
}

def has_permission(action_code: str) -> bool:
    """
    Checks if the currently selected department has the granular permission.
    In production, IT will replace this with a call to SAP (e.g., checking an Auth Object).
    """
    current_dept = st.session_state.get('department')
    if not current_dept:
        return False
    return action_code in ROLE_PERMISSIONS.get(current_dept, [])

# --- GLOBAL SHARED DATABASE MOCK ---
# We use a class and @st.cache_resource to create a global "Singleton"
# that is shared across ALL users and ALL browser tabs connected to the app.
class MockSAPDatabase:
    def __init__(self):
        self.df = pd.DataFrame({
            'TO': [345001, 345002, 345003],
            'HU': [801001, 801002, 801003],
            'Material': ['MAT-1001', 'MAT-1002', 'MAT-1003'],
            'Description': ['Vials', 'Caps', 'Labels'],
            'Source': ['A1-01-01', 'A1-01-02', 'B2-03-01'],
            'Destination': ['PSS-L1', 'PSS-L2', 'PSS-L1'],
            'Status': ['Open', 'Open', 'Open'],
            'Operator': ['', 'User.A', '']
        })
        
        self.pharma_df = pd.DataFrame({
            'TO': [346001, 346002, 346003],
            'Material': ['PH-201', 'PH-202', 'PH-203'],
            'Batch': ['B-0010', 'B-0011', 'B-0012'],
            'Quantity': [1, 1, 1],
            'Status': ['Open', 'Open', 'Open']
        })
        
        self.ordered_lots_df = pd.DataFrame([{
            'Timestamp': pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
            'Lot': 'B-0099',
            'Destination': 'Fabrication',
            'Status': 'Livré'
        }])

        locations = [f'STG-{i:02d}' for i in range(1, 51)]
        lots_1 = [f'B-0{np.random.randint(100, 200)}' if np.random.rand() > 0.3 else '' for _ in range(50)]
        lots_2 = [f'B-0{np.random.randint(200, 300)}' if (l != '' and np.random.rand() > 0.7) else '' for l in lots_1]
        destinations = [np.random.choice(['Ligne 1', 'Ligne 2', 'Ligne 3', 'Ligne 4', 'Déchet']) if l != '' else '' for l in lots_1]
        
        self.staging_df = pd.DataFrame({
            'Location': locations,
            'Lot 1': lots_1,
            'Lot 2': lots_2,
            'Destination': destinations
        })

        # --- Production Lines & PO Data ---
        self.lines = [f"Line {i}" for i in range(1, 10)] + ["Line 18", "Line 19", "Line 20"]
        self.po_data = {}
        for i, line in enumerate(self.lines):
            self.po_data[line] = {
                "po": f"PRD-100{45+i}",
                "materials": {
                    "MAT-1001 (Vials)": {"target": 10000, "confirmed": np.random.randint(2000, 8000)},
                    "MAT-1002 (Caps)": {"target": 10000, "confirmed": np.random.randint(1500, 8500)},
                    "MAT-1003 (Labels)": {"target": 10500, "confirmed": np.random.randint(1000, 9000)},
                    "Cellophane Roll": {"target": 50, "confirmed": np.random.randint(5, 45)},
                    "Packaging Tape": {"target": 20, "confirmed": np.random.randint(2, 18)},
                    "Glue Box": {"target": 5, "confirmed": np.random.randint(1, 4)}
                }
            }

@st.cache_resource
def get_global_database(_version="1.1"): # Increment this number to force-clear the cache
    """
    Returns a singleton instance of the mock database.

    The _version parameter is a trick to allow cache invalidation during development.
    If you change the structure of MockSAPDatabase, increment the version number
    to force Streamlit to create a new instance.
    """
    return MockSAPDatabase()

# Initialize connection to our global mock DB
sap_db = get_global_database()

def simulate_sap_push_event():
    """
    Simulates an external system (or another user) injecting a record
    into the global SAP database.
    """
    new_to_number = int(sap_db.df['TO'].max() + 1)
    new_hu_number = int(sap_db.df['HU'].max() + 1)
    
    new_record = pd.DataFrame([{
        'TO': new_to_number,
        'HU': new_hu_number,
        'Material': 'MAT-INJECT',
        'Description': 'Injected Material',
        'Source': 'RECV-ZONE',
        'Destination': 'PSS-L3',
        'Status': 'Open',
        'Operator': ''
    }])
    
    # Update the global database directly
    sap_db.df = pd.concat([sap_db.df, new_record], ignore_index=True)

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

    # --- Main Navigation Sidebar ---
    with st.sidebar:
        st.title(f"🏢 {department}")
        
        if 'menu_selection' not in st.session_state:
            st.session_state.menu_selection = "Transactions"

        menu = st.radio(
            "Menu",
            ("Transactions", "SAP Genius"),
            key="menu_selection"
        )

        if st.button("⬅️ Change Department", use_container_width=True):
            # Clear department and other session state to reset
            for key in list(st.session_state.keys()):
                if key not in ['gemini_api_key']: # Persist API key
                    del st.session_state[key]
            st.rerun()

        st.divider()
        st.subheader("🛠️ Dev Tools: Mock Event")
        st.write("Simulate SAP pushing a new Transfer Order to the app in real-time.")
        if st.button("Simulate Incoming SAP Event"):
            simulate_sap_push_event()
            st.rerun() # In a real WebSocket implementation, the JS component triggers this automatically

    # --- Content Area ---
    if st.session_state.menu_selection == "SAP Genius":
        sap_genius_chat()
    else: # Default to "Transactions"
        st.title(f"{department} Transactions")

        if department == "Packaging":
            # Tabs act as "transaction separators"
            tab_oc1, tab_manage_pos, tab_placeholder2 = st.tabs(["OC1 - Material Order", "Manage POs", "Onglet C"])

            with tab_oc1:
                st.subheader("Transaction OC1: Material Requirements (LP12 Simulation)")
                st.caption("Order materials or non-consumables for your packaging line.")

                # Row 1: Line, Active PO, and Source
                col1, col2, col3 = st.columns([1, 1, 2])
                with col1:
                    prod_line = st.selectbox("Line", sap_db.lines)
                with col2:
                    current_po = sap_db.po_data[prod_line]
                    st.markdown(f"<div style='margin-top: 2rem;'><b>Active PO:</b> <span style='color: #0078D4; font-family: monospace; font-size: 1.1em;'>{current_po['po']}</span></div>", unsafe_allow_html=True)
                with col3:
                    mat_type = st.radio("Material Source", ["BOM (COR3)", "Non-consumable"], horizontal=True)

                # Row 2: Material, Qty, COR3 Status
                col4, col5, col6 = st.columns([1.5, 1, 1.5])
                with col4:
                    if mat_type == "BOM (COR3)":
                        material = st.selectbox("Material", ["MAT-1001 (Vials)", "MAT-1002 (Caps)", "MAT-1003 (Labels)"])
                    else:
                        material = st.selectbox("Material", ["Cellophane Roll", "Packaging Tape", "Glue Box"])
                with col5:
                    qty_label = "Req. Qty (Pallets)" if mat_type == "BOM (COR3)" else "Req. Qty (Each)"
                    quantity = st.number_input(qty_label, min_value=1, step=1)
                with col6:
                    # Fetch material specific tracking
                    mat_data = current_po["materials"].get(material, {"target": 100, "confirmed": 0})
                    rem = mat_data['target'] - mat_data['confirmed']
                    progress_val = min(mat_data['confirmed'] / mat_data['target'], 1.0) if mat_data['target'] > 0 else 0.0
                    st.markdown(f"<div style='font-size:0.85em; margin-bottom: 4px; margin-top: 0.5rem;'><b>COR3 Prod. Status:</b> {mat_data['confirmed']} done | <b>{rem} left</b></div>", unsafe_allow_html=True)
                    st.progress(progress_val)

                # 5. Create Transfer Order (TO)
                # --- RBP IN ACTION ---
                # We check the granular permission before allowing the action.
                if has_permission("CREATE_PACKAGING_TO"):
                    if st.button("Create TO (Transfer Order)", type="primary"):
                        new_to_number = int(sap_db.df['TO'].max() + 1) if not sap_db.df.empty else 345000
                        max_hu = pd.to_numeric(sap_db.df['HU'], errors='coerce').max()
                        new_hu_number = int(max_hu + 1) if pd.notna(max_hu) else 801000
                        
                        if mat_type == "BOM (COR3)":
                            qty_desc = f"{quantity} Pallet(s)"
                            mat_code = material.split(" ")[0]
                            mat_name = material.split(' ', 1)[1] if ' ' in material else material
                        else:
                            qty_desc = f"{quantity} Each"
                            mat_code = "NON-BOM"
                            mat_name = material
                            
                        # Update the global state
                        new_record = pd.DataFrame([{
                            'TO': new_to_number,
                            'HU': new_hu_number if mat_type == "BOM (COR3)" else "N/A",
                            'Material': mat_code,
                            'Description': f"{qty_desc} of {mat_name} for {prod_line}",
                            'Source': 'PKG-REQ',
                            'Destination': 'PAD',
                            'Status': 'Open',
                            'Operator': 'Packaging'
                        }])
                        sap_db.df = pd.concat([sap_db.df, new_record], ignore_index=True)
                        
                        st.success(f"✅ Transfer Order {new_to_number} created successfully!")
                        st.info(f"**Action Executed:** {qty_desc} of {mat_name} requested for {prod_line}. Pallet redirection requested.")
                else:
                    st.button("Create TO (Transfer Order)", disabled=True, help="🔒 Missing SAP Authorization: CREATE_PACKAGING_TO")
                    st.error("You do not have the required SAP permissions to create packaging Transfer Orders.")

            with tab_manage_pos:
                st.subheader("Manage Active Process Orders")
                st.write("Bulk update the active Process Order (PO) running on each packaging line.")

                # Create a dataframe for the editor
                po_df = pd.DataFrame([
                    {"Line": line, "Active PO": data["po"]}
                    for line, data in sap_db.po_data.items()
                ])

                # Use st.data_editor to allow bulk changes directly in the UI table
                edited_po_df = st.data_editor(po_df, hide_index=True, use_container_width=True, disabled=["Line"])

                if st.button("Save PO Changes", type="primary"):
                    for index, row in edited_po_df.iterrows():
                        line = row["Line"]
                        new_po = row["Active PO"]
                        if sap_db.po_data[line]["po"] != new_po:
                            sap_db.po_data[line]["po"] = new_po
                            # Material confirmed counts could optionally be reset here if PO changes
                    st.success("Active POs updated successfully!")

        elif department == "Warehousing":
            tab_oe2_entrepot, tab_oe2_pharmacie, tab_oe1_caristes = st.tabs(["OE2 Entrepôt", "OE2 Pharmacie", "OE1 Caristes"])

            with tab_oe2_entrepot:
                st.subheader("OE2 Entrepôt : Commandes à Préparer (Pick PSS)")
                st.write("Cet écran simule une version simplifiée de la transaction LT22, utilisée pour la préparation des commandes de palettes complètes.")

                # --- LIVE POLLING COMPONENT ---
                # st.fragment with run_every will automatically re-run JUST this function
                # every 2 seconds, checking the global sap_db for updates.
                @st.fragment(run_every="2s")
                def live_monitoring_table():
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write("*(🟢 Live View - Auto-syncing with global server...)*")
                    with col2:
                        # Small toggle on the right to show only confirmed TOs
                        show_confirmed = st.toggle("Historique (30 derniers confirmés)")
                        
                    if show_confirmed:
                        df_to_show = sap_db.df[sap_db.df['Status'] == 'Confirmed'].tail(30)
                    else:
                        df_to_show = sap_db.df[sap_db.df['Status'] == 'Open']
                        
                    # Added height parameter to restrict table size and enable scrollbar
                    st.dataframe(df_to_show, use_container_width=True, height=250)

                live_monitoring_table()

                st.subheader("Confirmer un Pick (Simulation LT12 par scan)")
                scanned_hu = st.text_input("Scanner l'étiquette HU (ex: 801001):")
                
                # --- RBP IN ACTION ---
                if has_permission("CONFIRM_PICK_TO"):
                    if st.button("Confirmer le Pick", type="primary"):
                        if scanned_hu:
                            try:
                                hu_int = int(scanned_hu)
                                matching_rows = sap_db.df[(sap_db.df['HU'] == hu_int) & (sap_db.df['Status'] == 'Open')]
                                
                                if not matching_rows.empty:
                                    to_num = matching_rows.iloc[0]['TO']
                                    sap_db.df.loc[sap_db.df['TO'] == to_num, 'Status'] = 'Confirmed'
                                    st.success(f"✅ Pick confirmé pour le HU {hu_int} (TO: {to_num})!")
                                else:
                                    st.warning(f"❌ Aucun TO ouvert trouvé pour le HU {hu_int}.")
                            except ValueError:
                                st.error("Format de HU invalide. Veuillez entrer uniquement des chiffres.")
                    else:
                        st.warning("Veuillez scanner un HU avant de confirmer.")
                else:
                    st.button("Confirmer le Pick", disabled=True, help="🔒 Missing SAP Authorization: CONFIRM_PICK_TO")

                st.divider()
                st.subheader("Confirmer un Pick (Non-Consommables)")
                st.write("Les non-consommables ne nécessitent pas de scan HU. Confirmez-les manuellement :")
                
                open_non_bom = sap_db.df[(sap_db.df['Material'] == 'NON-BOM') & (sap_db.df['Status'] == 'Open')]
                
                if has_permission("CONFIRM_PICK_TO"):
                    if not open_non_bom.empty:
                        for _, row in open_non_bom.iterrows():
                            col_a, col_b = st.columns([4, 1])
                            with col_a:
                                st.markdown(f"**TO {row['TO']}** - {row['Description']} *(Dest: {row['Destination']})*")
                            with col_b:
                                if st.button("✔️ Confirmer", key=f"btn_{row['TO']}"):
                                    sap_db.df.loc[sap_db.df['TO'] == row['TO'], 'Status'] = 'Confirmed'
                                    st.toast(f"✅ TO {row['TO']} confirmé!")
                                    st.rerun()
                    else:
                        st.info("Aucune commande de non-consommable en attente.")
                else:
                    st.info("🔒 Vous n'avez pas l'autorisation de confirmer ces TOs.")

            with tab_oe2_pharmacie:
                st.subheader("OE2 Pharmacie : Sorties de matériel (Direction APH)")
                st.write("Liste des TOs créés par la pharmacie pour les sorties de matériel.")

                @st.fragment(run_every="2s")
                def live_pharma_table():
                    st.write("*(🟢 Live View - Auto-syncing with global server...)*")
                    st.dataframe(sap_db.pharma_df, use_container_width=True)

                live_pharma_table()
                
                st.subheader("Confirmer un TO (Simulation LT12)")
                open_pharma_tos = sap_db.pharma_df[sap_db.pharma_df['Status'] == 'Open']['TO']
                selected_to_pharma = st.selectbox("Sélectionner un TO à confirmer:", open_pharma_tos)

                if st.button("Confirmer le TO de la Pharmacie", type="primary"):
                    if selected_to_pharma:
                        sap_db.pharma_df.loc[sap_db.pharma_df['TO'] == selected_to_pharma, 'Status'] = 'Confirmed'
                        st.success(f"✅ TO {selected_to_pharma} confirmé!")
                    else:
                        st.warning("Aucun TO ouvert à confirmer.")


            with tab_oe1_caristes:
                st.subheader("OE1 Caristes : Gestion des Emplacements")

                sub_menu = st.radio("Navigation Cariste:", ["Commandes de Lots", "Entreposage Staging"], horizontal=True, label_visibility="collapsed")

                if sub_menu == "Commandes de Lots":
                    st.write("#### Commande de lots pour la fabrication")
                    col1, col2 = st.columns(2)
                    with col1:
                        lot_to_order = st.text_input("Entrer un numéro de lot à commander:")
                        if st.button("Commander le lot"):
                            if lot_to_order:
                                new_order = pd.DataFrame([{
                                    'Timestamp': pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
                                    'Lot': lot_to_order,
                                    'Destination': 'Fabrication',
                                    'Status': 'En transit'
                                }])
                                sap_db.ordered_lots_df = pd.concat([sap_db.ordered_lots_df, new_order], ignore_index=True)
                                st.success(f"Lot {lot_to_order} commandé pour la fabrication.")
                            else:
                                st.warning("Veuillez entrer un numéro de lot.")
                    with col2:
                        st.write("**Zones d'entreposage des palettes commandées:**")
                        st.text("Zone STG-A, STG-B, STG-C")
                        
                    st.divider()
                    st.write("#### Historique des commandes (Live)")
                    @st.fragment(run_every="2s")
                    def live_ordered_lots():
                        st.dataframe(sap_db.ordered_lots_df, use_container_width=True)
                    live_ordered_lots()


                elif sub_menu == "Entreposage Staging":
                    st.write("#### État de l'entreposage Staging (Locations 1-50)")

                    def style_destination(val):
                        color = ''
                        if not isinstance(val, str): return ''
                        if 'Ligne 1' in val: color = 'blue'
                        elif 'Ligne 2' in val: color = 'green'
                        elif 'Ligne 3' in val: color = 'orange'
                        elif 'Ligne 4' in val: color = 'purple'
                        elif 'Déchet' in val: color = 'red'
                        return f'color: {color}; font-weight: bold;'

                    @st.fragment(run_every="2s")
                    def live_staging_table():
                        st.write("*(🟢 Live View - Auto-syncing with global server...)*")
                        st.dataframe(
                            sap_db.staging_df.style.applymap(style_destination, subset=['Destination']),
                            use_container_width=True
                        )
                    live_staging_table()


        elif department == "Manufacturing":
            st.info("Manufacturing transactions are currently under construction.")
        elif department == "Management":
            st.info("Management transactions are currently under construction.")
