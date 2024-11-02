import streamlit as st
from groq import Groq

# Set up page configuration for better presentation
st.set_page_config(
    page_title="RecipEase",
    page_icon="🍲",
    layout="centered",
    initial_sidebar_state="auto",
)

# Custom CSS for styling
st.markdown(
    """
    <style>
    .title {
        font-family: 'Arial', sans-serif;
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
        background-color: #f9f9f9;
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        font-size: 16px;
        color: #333;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Display title, logo, and description
st.markdown("<h1 class='title'>RecipEase</h1>", unsafe_allow_html=True)
st.image("recipeclip.jpg", width=120)
st.markdown("Welcome to **RecipEase**! Enter ingredients you have, and get recipes instantly.")

# User Input Section
st.markdown("### Enter Ingredients:")
user_ingredients = st.text_input("Which Ingredients Do You Have?", placeholder="e.g., chicken, broccoli, garlic", help="List ingredients separated by commas.")

# Initialize the Groq API client
client = Groq(api_key="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")

# Sidebar for extra options (optional, for additional functionality)
st.sidebar.header("Settings")
st.sidebar.write("Adjust your preferences here.")
st.sidebar.slider("Adjust Recipe Complexity:", 1, 5, 3)
cuisine = st.sidebar.selectbox("Select Cuisine Type", ["Any", "Italian", "Chinese", "Mexican", "Indian", "Mediterranean"])

# Define a function to get recipe recommendations
def get_recipe_recommendation(ingredients):
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system","content": "Based on the user input, respond with just list of recipes containing those ingredients, and also list out what other ingredients would be needed to make that recipe. don't respond with anything else."},
            {"role": "user", "content": ingredients + cuisine},
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
        # Display recipe in a styled container
        st.markdown("<div class='recipe-container'>" + recipe + "</div>", unsafe_allow_html=True)
    else:
        st.warning("Please enter at least one ingredient.")


