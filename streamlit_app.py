import streamlit as st
from openai import OpenAI
from groq import Groq

# Show title and description.
st.title("RecipEase")
user_ingredients = st.text_input("Which Ingredients Do You Have?", )

client = Groq(
    api_key= "xxxxxxxxxxxxx",
)

chat_completion = client.chat.completions.create(
    #
    # Required parameters
    #
    messages=[
        # Set an optional system message. This sets the behavior of the
        # assistant and can be used to provide specific instructions for
        # how it should behave throughout the conversation.
        {
            "role": "system",
            "content": "You know everything about recipes and food, and can give helpful recipes and cooking advice."
        },
        # Set a user message for the assistant to respond to.
        {
            "role": "user",
            "content": user_ingredients,
        }
    ],

    # The language model which will generate the completion.
    model="llama3-8b-8192",

    #
    # Optional parameters
    #

    # Controls randomness: lowering results in less random completions.
    # As the temperature approaches zero, the model will become deterministic
    # and repetitive.
    temperature=0.5,

    # The maximum number of tokens to generate. Requests can use up to
    # 32,768 tokens shared between prompt and completion.
    max_tokens=1024,

    # Controls diversity via nucleus sampling: 0.5 means half of all
    # likelihood-weighted options are considered.
    top_p=1,

    # A stop sequence is a predefined or user-specified text string that
    # signals an AI to stop generating content, ensuring its responses
    # remain focused and concise. Examples include punctuation marks and
    # markers like "[end]".
    stop=None,

    # If set, partial message deltas will be sent.
    stream=False,
)
# Print the completion returned by the LLM.
if(user_ingredients is not (None or "")):
    st.write(chat_completion.choices[0].message.content)