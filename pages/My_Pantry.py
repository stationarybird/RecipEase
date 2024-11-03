import streamlit as st
import streamlit_authenticator as stauth
import yaml
import json
import os
from yaml.loader import SafeLoader

# Define paths for settings and pantry data storage
SETTINGS_FILE = 'user_settings.json'
PANTRY_FILE = 'user_pantry.json'

def load_pantry():
    """Load pantry items from a JSON file."""
    if os.path.exists(PANTRY_FILE):
        with open(PANTRY_FILE, 'r') as f:
            return json.load(f)
    return []

def save_pantry(pantry_items):
    """Save pantry items to a JSON file."""
    with open(PANTRY_FILE, 'w') as f:
        json.dump(pantry_items, f)


try:
    with open('config.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)
except FileNotFoundError:
    st.error("Configuration file 'confid.yaml' not found.")
    st.stop()

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)


if st.session_state['authentication_status']:
    st.sidebar.write(f"Welcome **{st.session_state["name"]}**!")
    st.sidebar.page_link("streamlit_app.py", label="Home", icon="🏠")
    st.sidebar.page_link("pages/settings.py", label="Settings", icon="⚙️")
    st.sidebar.page_link("pages/My_Pantry.py", label="My Pantry", icon="🚪")
    st.sidebar.page_link("pages/history.py", label="History", icon="📖")
    st.header("Your Pantry")
    st.write("Save your ingredients here and RecipEase will help you out!")

    pantry_items = load_pantry()

if st.session_state['authentication_status']:
    st.sidebar.write(f"Welcome **{st.session_state['name']}**!")
    st.sidebar.write("My Pantry")


    # Display existing pantry items
    if pantry_items:
        st.subheader("Your Current Ingredients")
        for item in pantry_items:
            st.write(f"- {item}")

    # Input to add new ingredients
    new_ingredient = st.text_input("Add an ingredient to your pantry:", placeholder="e.g., tomatoes, garlic")
    if st.button("Add Ingredient"):
        if new_ingredient:
            pantry_items.append(new_ingredient)
            save_pantry(pantry_items)  # Save the updated pantry
            st.success(f"{new_ingredient} added to pantry!")

    # Option to remove an ingredient
    ingredient_to_remove = st.selectbox("Select an ingredient to remove:", options=pantry_items, index=0) if pantry_items else None
    if st.button("Remove Ingredient") and ingredient_to_remove:
        pantry_items = [item for item in pantry_items if item != ingredient_to_remove]
        save_pantry(pantry_items)  # Save updated pantry after removal
        st.success(f"{ingredient_to_remove} removed from pantry!")

    for i in range(15):
        st.sidebar.write('\n')
        i = i - 1 
    authenticator.logout('Logout', 'sidebar')
