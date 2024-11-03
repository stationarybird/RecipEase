import streamlit as st
from groq import Groq
import streamlit_authenticator as stauth
import os
import yaml
from yaml.loader import SafeLoader

# # List of plain text passwords
# passwords = ['abc', 'def']


# # Hash the passwords
# hasher = stauth.Hasher(passwords)
# hash_passwords = hasher.hash_list()

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
    authenticator.logout()
    st.write(f'Welcome *{st.session_state["name"]}*')
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
        color: #f9f9f9
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if st.session_state['authentication_status']:
    # Display title, logo, and description
    st.markdown("<h1 class='title'>RecipEase</h1>", unsafe_allow_html=True)
    # st.image("recipeclip.jpg", width=120)
    st.markdown( "<p style='text-align: center;'>Welcome to <strong>RecipEase</strong>! Enter ingredients you have, and get recipes instantly.</p>",  unsafe_allow_html=True)
    st.divider()

    # User Input Section
    st.markdown("### Enter Ingredients:")

    # Initialize the Groq API client
    client = Groq(api_key="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")

    restrictions = st.sidebar.multiselect("What are your dietary restrictions?",["Vegetarian", "Vegan", "Lactose Intolerant", "Halal", "Gluten Free", "No Soy", "Other (specify below)"], placeholder="Select preset restrictions here...",)
    
    if restrictions and restrictions[-1] == "Other (specify below)":
        custom_restriction = st.sidebar.text_input(
            "Add Custom Dietary Restriction (if any):",
            placeholder="e.g., Peanuts, Strawberries",
        )
        # Append custom restriction only if it was entered
        if custom_restriction:
            restrictions.append("None of these: " + custom_restriction)

    # Sidebar for extra options (optional, for additional functionality)
    st.sidebar.header("Settings")
    st.sidebar.write("Adjust your preferences here.")
    complexity = st.sidebar.slider("Adjust Recipe Complexity:", 1, 5, 3)
    cuisine = st.sidebar.selectbox("Select Cuisine Type", ["Any", "Italian", "Chinese", "Mexican", "Indian", "Mediterranean"])
    user_ingredients = st.text_area("Which Ingredients Do You Have?", placeholder="e.g., chicken, broccoli, garlic", help="List ingredients separated by commas.")

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
                keep in mind their allergies and dietary restrictions and make sure these are definitely not in the recipes. 
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

    # Display the recipe instructions if available
    if 'recipe_instructions' in st.session_state:
        st.markdown("<div class='recipe-container'>" + st.session_state.recipe_instructions + "</div>", unsafe_allow_html=True)

        respond = st.checkbox("Would you like to see the nutritional information for this recipe?")

        if respond and st.button("Get Nutritional Information", key="btn-nutrition"):
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


