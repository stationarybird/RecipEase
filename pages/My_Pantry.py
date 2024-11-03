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
    st.sidebar.page_link("pages/My_Pantry.py", label="My Pantry", icon="🚪")
    st.sidebar.page_link("pages/history.py", label="History", icon="📖")
    st.header("Your Pantry")
    st.write("Save your ingredients here and RecipEase will help you out!")
