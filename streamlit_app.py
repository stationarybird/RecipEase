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
#st.image("recipeclip.jpg", width=120)
st.markdown( "<p style='text-align: center;'>Welcome to <strong>RecipEase</strong>! Enter ingredients you have, and get recipes instantly.</p>",  unsafe_allow_html=True)
st.divider()

# User Input Section
st.markdown("### Enter Ingredients:")


# Initialize the Groq API client
client = Groq(api_key="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")

# Sidebar for extra options (optional, for additional functionality)
st.sidebar.header("Settings")
st.sidebar.write("Adjust your preferences here.")
st.sidebar.slider("Adjust Recipe Complexity:", 1, 5, 3)

restrictions = st.sidebar.multiselect("What are your dietary restrictions?",["Vegetarian", "Vegan", "Lactose Intolerant", "Halal", "Gluten Free", "No Soy", "Other (specify below)"], placeholder="Select preset restrictions here...",)

if restrictions and restrictions[-1] == "Other (specify below)":
    custom_restriction = st.sidebar.text_input(
        "Add Custom Dietary Restriction (if any):",
        placeholder="e.g., Peanuts, Strawberries",
    )
    # Append custom restriction only if it was entered
    if custom_restriction:
        restrictions.append("None of these: " + custom_restriction)

cuisine = st.sidebar.selectbox("Select Cuisine Type", ["Any", "Italian", "Chinese", "Mexican", "Indian", "Mediterranean"])
user_ingredients = st.text_area("Which Ingredients Do You Have?", placeholder="e.g., chicken, broccoli, garlic", help="List ingredients separated by commas.")

# Define a function to get recipe recommendations
def get_recipe_recommendation(ingredients):
    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system","content": "Based on the user input, respond with just list of recipes containing those ingredients, and also list out what other ingredients would be needed to make that recipe. additionally, write out the instructions to make each dish. keep in mind their allergies and dietary restrictions and make sure these are not in the recipes. if an ingredient is mentioned that is restricted, make sure you explicilty state that you will not include it in the recipes you generate.  don't respond with anything else."},
            {"role": "user", "content": ingredients + cuisine + str(restrictions)},
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


