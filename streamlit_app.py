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


    # --- Content Area ---
    if st.session_state.menu_selection == "SAP Genius":
        sap_genius_chat()
    else: # Default to "Transactions"
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
            tab_oe2_entrepot, tab_oe2_pharmacie, tab_oe1_caristes = st.tabs(["OE2 Entrepôt", "OE2 Pharmacie", "OE1 Caristes"])

            with tab_oe2_entrepot:
                st.subheader("OE2 Entrepôt : Commandes à Préparer (Pick PSS)")
                st.write("Cet écran simule une version simplifiée de la transaction LT22, utilisée pour la préparation des commandes de palettes complètes.")

                if st.button("Rafraîchir les données"):
                    st.rerun()

                # --- Sample Data ---
                data = {
                    'TO': [345001, 345002, 345003, 345004, 345005],
                    'HU': [801001, 801002, 801003, 801004, 801005],
                    'Material': ['MAT-1001', 'MAT-1002', 'MAT-1003', 'SR-244', 'SR-245'],
                    'Description': ['Vials', 'Caps', 'Labels', 'Syringes', 'Alcohol Wipes'],
                    'Source': ['A1-01-01', 'A1-01-02', 'B2-03-01', 'C4-02-03', 'D1-05-01'],
                    'Destination': ['PSS-L1', 'PSS-L2', 'PSS-L1', 'PSS-L3', 'PSS-L4'],
                    'Status': ['Open', 'Open', 'Open', 'Open', 'Open'],
                    'Operator': ['', 'User.A', '', 'User.B', '']
                }
                df_entrepot = pd.DataFrame(data)
                
                st.dataframe(df_entrepot, use_container_width=True)

                st.subheader("Confirmer un TO (Simulation LT12)")
                selected_to = st.selectbox("Sélectionner un TO à confirmer:", df_entrepot['TO'])
                
                if st.button("Confirmer le Pick du TO", type="primary"):
                    st.success(f"✅ TO {selected_to} confirmé!")
                    st.info(f"La palette HU {df_entrepot[df_entrepot['TO'] == selected_to]['HU'].values[0]} a été déplacée vers la zone PAD.")


            with tab_oe2_pharmacie:
                st.subheader("OE2 Pharmacie : Sorties de matériel (Direction APH)")
                st.write("Liste des TOs créés par la pharmacie pour les sorties de matériel.")

                if st.button("Rafraîchir les données "): #space to avoid duplicate key error
                    st.rerun()

                # --- Sample Data ---
                data_pharma = {
                    'TO': [346001, 346002, 346003],
                    'Material': ['PH-201', 'PH-202', 'PH-203'],
                    'Batch': ['B-0010', 'B-0011', 'B-0012'],
                    'Quantity': [1, 1, 1],
                    'Status': ['Open', 'Open', 'Open']
                }
                df_pharma = pd.DataFrame(data_pharma)
                st.dataframe(df_pharma, use_container_width=True)
                
                st.subheader("Confirmer un TO (Simulation LT12)")
                selected_to_pharma = st.selectbox("Sélectionger un TO à confirmer:", df_pharma['TO'])

                if st.button("Confirmer le TO de la Pharmacie", type="primary"):
                    st.success(f"✅ TO {selected_to_pharma} confirmé!")


            with tab_oe1_caristes:
                st.subheader("OE1 Caristes : Gestion des Emplacements")

                sub_menu = st.radio("Navigation Cariste:", ["Commandes de Lots", "Entreposage Staging"], horizontal=True, label_visibility="collapsed")

                if sub_menu == "Commandes de Lots":
                    st.write("#### Commande de lots pour la fabrication")
                    col1, col2 = st.columns(2)
                    with col1:
                        lot_to_order = st.text_input("Entrer un numéro de lot à commander:")
                        if st.button("Commander le lot"):
                            st.success(f"Lot {lot_to_order} commandé pour la fabrication.")
                    with col2:
                        st.write("**Zones d'entreposage des palettes commandées:**")
                        st.text("Zone STG-A, STG-B, STG-C")


                elif sub_menu == "Entreposage Staging":
                    st.write("#### État de l'entreposage Staging (Locations 1-50)")

                    # --- Sample Data ---
                    locations = [f'STG-{i:02d}' for i in range(1, 51)]
                    lots_1 = [f'B-0{np.random.randint(100, 200)}' if np.random.rand() > 0.3 else '' for _ in range(50)]
                    lots_2 = [f'B-0{np.random.randint(200, 300)}' if (l != '' and np.random.rand() > 0.7) else '' for l in lots_1]
                    destinations = [np.random.choice(['Ligne 1', 'Ligne 2', 'Ligne 3', 'Ligne 4', 'Déchet']) if l != '' else '' for l in lots_1]
                    
                    df_staging = pd.DataFrame({
                        'Location': locations,
                        'Lot 1': lots_1,
                        'Lot 2': lots_2,
                        'Destination': destinations
                    })

                    def style_destination(val):
                        color = ''
                        if 'Ligne 1' in val: color = 'blue'
                        elif 'Ligne 2' in val: color = 'green'
                        elif 'Ligne 3' in val: color = 'orange'
                        elif 'Ligne 4' in val: color = 'purple'
                        elif 'Déchet' in val: color = 'red'
                        return f'color: {color}; font-weight: bold;'

                    st.dataframe(
                        df_staging.style.applymap(style_destination, subset=['Destination']),
                        use_container_width=True
                    )


        elif department == "Manufacturing":
            st.info("Manufacturing transactions are currently under construction.")
        elif department == "Management":
            st.info("Management transactions are currently under construction.")
