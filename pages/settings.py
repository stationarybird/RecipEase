import streamlit as st
from groq import Groq
import streamlit_authenticator as stauth
import os
import yaml
import json
from yaml.loader import SafeLoader

# Define path for storing settings
SETTINGS_FILE = 'user_settings.json'

def load_settings():
    """Load settings from a JSON file."""
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_settings(settings):
    """Save settings to a JSON file."""
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f)


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

settings = load_settings()


if st.session_state['authentication_status']:
    st.sidebar.write(f"Welcome **{st.session_state['name']}**!")
    st.sidebar.page_link("streamlit_app.py", label="Home", icon="🏠")
    st.sidebar.page_link("pages/settings.py", label="Settings", icon="⚙️")
    st.sidebar.page_link("pages/history.py", label="History", icon="📖")
    st.header("Settings")
    st.write("Adjust your preferences here.")

    complexity = st.slider(
        "Adjust Recipe Complexity:", 
        1, 
        5, 
        settings.get('complexity', 3)
    )
    st.session_state['complexity'] = complexity

    restrictions = st.multiselect(
        "What are your dietary restrictions?",
        ["Vegetarian", "Vegan", "Lactose Intolerant", "Halal", "Gluten Free", "No Soy", "Other (specify below)"],
        default=settings.get('restrictions', [])
    )
    if restrictions and restrictions[-1] == "Other (specify below)":
        custom_restriction = st.text_input(
            "Add Custom Dietary Restriction (if any):",
            placeholder="e.g., Peanuts, Strawberries"
        )
        if custom_restriction:
            restrictions.append("None of these: " + custom_restriction)
    st.session_state['restrictions'] = restrictions
    

    cuisine = st.selectbox(
        "Select Cuisine Type", 
        ["Any", "Italian", "Chinese", "Mexican", "Indian", "Mediterranean"], 
        index=["Any", "Italian", "Chinese", "Mexican", "Indian", "Mediterranean"].index(settings.get('cuisine', "Any"))
    )
    st.session_state['cuisine'] = cuisine

    for i in range(15):
        st.sidebar.write('\n')
        i = i - 1 
    authenticator.logout('Logout', 'sidebar')

    save_settings({
        'complexity': complexity,
        'restrictions': restrictions,
        'cuisine': cuisine
    })

   