import streamlit as st
from groq import Groq
import streamlit_authenticator as stauth
import os
import yaml
from yaml.loader import SafeLoader
import sqlite3

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

# Function to fetch past queries from the database
def get_user_history(username):
    with sqlite3.connect('users.db') as conn:
        c = conn.cursor()
        c.execute('''
            SELECT ingredient_search, restrictions, complexity_level, cuisine, timestamp
            FROM user_data
            WHERE username = ?
            ORDER BY timestamp DESC
            LIMIT 10
        ''', (username,))
        return c.fetchall()

if st.session_state['authentication_status']:
    st.sidebar.write(f"Welcome **{st.session_state['name']}**!")
    st.sidebar.page_link("streamlit_app.py", label="Home", icon="🏠")
    st.sidebar.page_link("pages/settings.py", label="Settings", icon="⚙️")
    st.sidebar.page_link("pages/history.py", label="History", icon="📖")
    st.header("History")
    # Display history button and retrieve history on click
    history = get_user_history(st.session_state['name'])
    if history:
        for search in history:
            ingredients, restrictions, complexity, cuisine, timestamp = search
            st.write(
                f"**{timestamp}**\n- Ingredients: {ingredients}\n- Restrictions: {restrictions}\n- Complexity: {complexity}\n- Cuisine: {cuisine}"
            )
    else:
        st.write("No history found.")

    for i in range(15):
        st.sidebar.write('\n')
        i = i - 1 
    authenticator.logout('Logout', 'sidebar')
else:
    st.write("Please log in to view your history.")



   