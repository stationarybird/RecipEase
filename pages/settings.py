import streamlit as st
from groq import Groq
import streamlit_authenticator as stauth
import os
import yaml
from yaml.loader import SafeLoader

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

try:
    with open('config.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)
except FileNotFoundError:
    st.error("Configuration file 'confid.yaml' not found.")
    st.stop()

if st.session_state['authentication_status']:
    st.sidebar.write(f"Welcome **{st.session_state["name"]}**!")
    st.sidebar.page_link("streamlit_app.py", label="Home", icon="🏠")
    st.sidebar.page_link("pages/settings.py", label="Settings", icon="⚙️")
    st.header("Settings")
    st.write("Adjust your preferences here.")

    complexity = st.slider("Adjust Recipe Complexity:", 1, 5, 3)
    st.session_state['complexity'] = complexity
    restrictions = st.multiselect("What are your dietary restrictions?",["Vegetarian", "Vegan", "Lactose Intolerant", "Halal", "Gluten Free", "No Soy", "Other (specify below)"], placeholder="Select preset restrictions here...",)
    if restrictions and restrictions[-1] == "Other (specify below)":
        custom_restriction = st.text_input(
            "Add Custom Dietary Restriction (if any):",
            placeholder="e.g., Peanuts, Strawberries",
        )
        # Append custom restriction only if it was entered
        if custom_restriction:
            restrictions.append("None of these: " + custom_restriction)
    st.session_state['restrictions'] = restrictions
    
    cuisine = st.selectbox("Select Cuisine Type", ["Any", "Italian", "Chinese", "Mexican", "Indian", "Mediterranean"])
    st.session_state['cuisine'] = cuisine

    for i in range(15):
        st.sidebar.write('\n')
        i = i - 1 
    authenticator.logout('Logout', 'sidebar')

   