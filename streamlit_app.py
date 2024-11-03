import streamlit as st
from groq import Groq
import os
import tensorflow as tf
from tensorflow.keras.preprocessing.image import load_img, img_to_array
from tensorflow.keras.applications.resnet50 import preprocess_input, decode_predictions
import numpy as np

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
uploaded_file = st.file_uploader("Upload an image of your ingredients", type=["jpg", "jpeg", "png"])

# Path to the saved model file
model_path = "food101_model.h5"
model = tf.keras.models.load_model(model_path)

def prepare_image(image_path):
    img = load_img(image_path, target_size=(224, 224))  # Resize image to 224x224
    img_array = img_to_array(img)  # Convert to numpy array
    img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
    return preprocess_input(img_array)  # Preprocess the image

def detect_ingredients(image_path):
    img = prepare_image(image_path)
    preds = model.predict(img)  # Predict with the model
    decoded_preds = decode_predictions(preds, top=5)[0]  # Decode predictions
    ingredients = [(label, round(confidence * 100, 2)) for _, label, confidence in decoded_preds]
    return ingredients

if uploaded_file is not None:
    with open("temp_image.jpg", "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    # Call the ingredient detection function
    ingredients_probs = detect_ingredients("temp_image.jpg")

    ingredients = [(class_labels[i], round(ingredients_probs[i] * 100, 2)) for i in np.argsort(ingredients_probs)[-5:]]
    
    # Display the detected ingredients
    st.write("Detected Ingredients:")
    for ingredient, confidence in ingredients:
        st.write(f"{ingredient}: {confidence}%")


# Initialize the Groq API client
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

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


