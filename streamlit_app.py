import streamlit as st
from groq import Groq
import streamlit_authenticator as stauth
import os
import tensorflow as tf
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from tensorflow.keras.applications.resnet50 import preprocess_input, decode_predictions
import numpy as np
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
    st.sidebar.write(f"Welcome **{st.session_state['name']}**!")
    st.sidebar.page_link("streamlit_app.py", label="Home", icon="🏠")
    st.sidebar.page_link("pages/settings.py", label="Settings", icon="⚙️")
    st.sidebar.page_link("pages/My_Pantry.py", label="My Pantry", icon="🚪")
    st.sidebar.page_link("pages/history.py", label="History", icon="📖")
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

    # st.image("recipeclip.jpg", width=120)
    st.markdown( "<p style='text-align: center;'>Welcome to <strong>RecipEase</strong>! Enter ingredients you have, and get recipes instantly.</p>",  unsafe_allow_html=True)
    st.divider()

    # User Input Section
    st.markdown("### Enter Ingredients:")
uploaded_file = st.file_uploader("Upload an image of your ingredients", type=["jpg", "jpeg", "png"])

# Path to the saved model file
model_path = "food101_model.h5"
model = tf.keras.models.load_model(model_path)


with open("classes.txt", "r") as f:
    class_labels = [line.strip() for line in f]

def prepare_image(image_path):
    img = load_img(image_path, target_size=(224, 224))  # Resize image to 224x224
    img_array = img_to_array(img)  # Convert to numpy array
    img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
    return preprocess_input(img_array)  # Preprocess the image

def detect_ingredients(image_path):
    img = prepare_image(image_path)
    preds = model.predict(img)[0]  # Predict with the model
    top_indices = preds.argsort()[-3:][::-1]  # Decode predictions
    ingredients = [(class_labels[i], preds[i] * 100) for i in top_indices]
    return ingredients

if uploaded_file is not None:
    with open("temp_image.jpg", "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    # Call the ingredient detection function
    ingredients_probs = detect_ingredients("temp_image.jpg")

    
    # Display the detected ingredients
    st.write("Detected Ingredients:")
    for ingredient, confidence in ingredients_probs:
        st.write(f"{ingredient}: {confidence}%")


    # Initialize the Groq API client
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

    
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
                {"role": "system","content": """Based on the user input, respond with just list of recipes containing those 
                ingredients, and also list out what other ingredients would be needed to make that recipe. 
                keep in mind and explicity declare their allergies and dietary restrictions and make sure these are definitely not in the recipes.
                If applicable, mention their chosen cuisine. 
                if an ingredient is mentioned that is restricted, make sure you explicilty state that you will not include 
                it in the recipes you generate. take into account the complexity level the user gives. don't respond with anything else."""},
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

    def get_recipe_instructions(recipeNum, rlist):
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system","content": """Write out the instructions to make the recipe of the number given from the recipe list. 
                keep in mind their allergies and dietary restrictions and make sure these are definitely not in the recipes. 
                take into account the complexity level the user gives. don't respond with anything else."""},
                {"role": "user", "content": rlist + recipeNum + str(restrictions) + recipeComplexity(complexity)},
            ],
            model="llama3-8b-8192",
            temperature=0.5,
            max_tokens=1024,
            top_p=1,
            stop=None,
            stream=False,
        )
        return chat_completion.choices[0].message.content

    def get_recipe_nutrition(recipe):
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system","content": """Write out the nutritional information of the recipe given above. don't respond with anything else."""},
                {"role": "user", "content": recipe},
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
                st.session_state.recipe = get_recipe_recommendation(user_ingredients)
                # Store user data
                if st.session_state.get('authentication_status'):
                    store_user_data(
                        st.session_state['name'], 
                        user_ingredients, 
                        restrictions, 
                        complexity, 
                        cuisine
                    )
            #st.markdown("<div class='recipe-container'>" + recipe + "</div>", unsafe_allow_html=True)
        else:
            st.warning("Please enter at least one ingredient.")
    
    if 'recipe' in st.session_state:
        # Display the recipe list in a styled container
        st.markdown("<div class='recipe-container'>" + st.session_state.recipe + "</div>", unsafe_allow_html=True)

        user_recipe = st.text_area("What Recipe do you want?", placeholder="Enter the recipe number or name from the list above.", help="Specify the recipe for which you want instructions.")
        if st.button("Get Recipe Instructions", key="btn-instruction"):
            if user_recipe:
                with st.spinner("Finding instructions..."):
                    recipe_instructions = get_recipe_instructions(user_recipe, st.session_state.recipe)
                # Store the instructions in session state for consistent display
                st.session_state.recipe_instructions = recipe_instructions
            else:
                st.warning("Please specify which recipe you want instructions for.")
    
    #Display the recipe instructions if available
    if 'recipe_instructions' in st.session_state:
        st.markdown("<div class='recipe-container'>" + st.session_state.recipe_instructions + "</div>", unsafe_allow_html=True)

        respond = st.button("Would you like to see the nutritional information for this recipe?")

        if respond:
            if 'recipe_instructions' in st.session_state:
                with st.spinner("Fetching nutritional information..."):
                    nutrition_info = get_recipe_nutrition(st.session_state.recipe_instructions)
                # Store nutritional info in session state to persist and display
                st.session_state.nutrition_info = nutrition_info
            else:
                st.warning("Please retrieve the recipe instructions first.")

        # Display the nutritional information if available in session state
        if 'nutrition_info' in st.session_state:
            st.markdown("<div class='recipe-container'>" + st.session_state.nutrition_info + "</div>", unsafe_allow_html=True)


