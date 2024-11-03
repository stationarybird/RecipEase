import streamlit as st
from groq import Groq
import streamlit_authenticator as stauth
import os
import yaml
from yaml.loader import SafeLoader
import sqlite3
from datetime import datetime

conn = sqlite3.connect('users.db')
c = conn.cursor()

c.execute('''
    CREATE TABLE IF NOT EXISTS user_data (
        username TEXT,
        ingredient_search TEXT,
        restrictions TEXT,
        complexity_level INTEGER,
        cuisine TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
''')
conn.commit()

def store_user_data(username, ingredients, restrictions, complexity, cuisine):
    # Insert user data into the database
    c.execute('''
        INSERT INTO user_data (username, ingredient_search, restrictions, complexity_level, cuisine)
        VALUES (?, ?, ?, ?, ?)
    ''', (username, ingredients, ', '.join(restrictions), complexity, cuisine))
    conn.commit()

# Load YAML configuration
try:
    with open('config.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)
except FileNotFoundError:
    st.error("Configuration file 'confid.yaml' not found.")
    st.stop()

# Set up page configuration for better presentation
st.set_page_config(
    page_title="RecipEase",
    page_icon="🍲",
    layout="centered",
    initial_sidebar_state="auto",
)

# Initialize the authenticator
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

# Login Widgets
try:
    authenticator.login()
except Exception as e:
    st.error(e)

if st.session_state['authentication_status']:
    st.sidebar.write(f"Welcome **{st.session_state["name"]}**!")
    st.sidebar.page_link("streamlit_app.py", label="Home", icon="🏠")
    st.sidebar.page_link("pages/settings.py", label="Settings", icon="⚙️")
elif st.session_state['authentication_status'] is False:
    st.error('Username/password is incorrect')
elif st.session_state['authentication_status'] is None:
    st.warning('Please enter your username and password')


# Custom CSS for styling
st.markdown(
    """
    <style>
    .title {
        font-family: 'Bradley Hand', cursive;
        color: #ff6347; /* Tomato color for a pop */
        text-align: center;
    }
    .ingredient-input {
        font-size: 18px;
        padding: 10px;
        margin-top: 10px;
    }
    .btn-style {
        background-color: #4CAF50; /* Green button */
        color: white;
        padding: 10px 20px;
        font-size: 16px;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        display: block;
        margin: auto;
    }
    .recipe-container {
        background-color: #262730;
        border: 1px solid #ff6347;
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        font-size: 16px;
        color: #ffffff;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

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
    # Display title, logo, and description
    st.markdown("<h1 class='title'>RecipEase</h1>", unsafe_allow_html=True)
    # Display history button and retrieve history on click
    if st.sidebar.button("Show History"):
        if st.session_state.get('authentication_status'):
            history = get_user_history(st.session_state['name'])
            if history:
                st.sidebar.markdown("### Search History")
                for search in history:
                    ingredients, restrictions, complexity, cuisine, timestamp = search
                    st.sidebar.write(
                        f"**{timestamp}**\n- Ingredients: {ingredients}\n- Restrictions: {restrictions}\n- Complexity: {complexity}\n- Cuisine: {cuisine}"
                    )
            else:
                st.sidebar.write("No history found.")
        else:
            st.sidebar.write("Please log in to view your history.")

    # st.image("recipeclip.jpg", width=120)
    st.markdown( "<p style='text-align: center;'>Welcome to <strong>RecipEase</strong>! Enter ingredients you have, and get recipes instantly.</p>",  unsafe_allow_html=True)
    st.divider()

    # User Input Section
    st.markdown("### Enter Ingredients:")

    # Initialize the Groq API client
    client = Groq(api_key="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")

    
    # Sidebar for extra options (optional, for additional functionality)
    user_ingredients = st.text_area("Which Ingredients Do You Have?", placeholder="e.g., chicken, broccoli, garlic", help="List ingredients separated by commas.")
    complexity = st.session_state.get('complexity', 3)
    restrictions = st.session_state.get('restrictions', [])
    cuisine = st.session_state.get('cuisine', "Any")

    for i in range(15):
        st.sidebar.write('\n')
        i = i - 1 
    authenticator.logout('Logout', 'sidebar')

    def recipeComplexity(complexity):
        match complexity:
            case 1:
                return "Very Easy"
            case 2:
                return "Easy"
            case 3: 
                return "Medium"
            case 4:
                return "Hard"
            case 5: 
                return "Very Hard"
            case _:
                return "Anything"   # Medium is the default case if complexity doesn't match anything

    # Define a function to get recipe recommendations
    def get_recipe_recommendation(ingredients):
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system","content": "Based on the user input, respond with just list of recipes containing those ingredients, and also list out what other ingredients would be needed to make that recipe. additionally, write out the instructions to make each dish. keep in mind their allergies and dietary restrictions and make sure these are not in the recipes. if an ingredient is mentioned that is restricted, make sure you explicilty state that you will not include it in the recipes you generate. take into account the complexity level the user gives don't respond with anything else."},
                {"role": "user", "content": ingredients + cuisine + str(restrictions) + recipeComplexity(complexity)},
            ],
            model="llama3-8b-8192",
            temperature=0.5,
            max_tokens=1024,
            top_p=1,
            stop=None,
            stream=False,
        )
        return chat_completion.choices[0].message.content

    # Button to submit and get recipe recommendations
    if st.button("Get Recipe Recommendation", key="btn-recipe"):
        if user_ingredients:
            with st.spinner("Finding recipes..."):
                recipe = get_recipe_recommendation(user_ingredients)
                # Store user data
                if st.session_state.get('authentication_status'):
                    store_user_data(
                        st.session_state['name'], 
                        user_ingredients, 
                        restrictions, 
                        complexity, 
                        cuisine
                    )
            st.markdown("<div class='recipe-container'>" + recipe + "</div>", unsafe_allow_html=True)
        else:
            st.warning("Please enter at least one ingredient.")


