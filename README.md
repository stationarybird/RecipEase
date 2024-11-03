**RecipEase**


The goal of this project is to create an application that allows users to enter common ingredients they want to create a recipe out of and output a list of famous recipes that incorporate those ingredients.

RecipEase makes cooking easy giving you a personalized experience based on what's in your kitchen and diet. From cuisine to the level of difficulty, RecipEase will help you level up your cooking!

* About the project
Be sure to write what inspired you, what you learned, how you built your project, and the challenges you faced. Format your story in Markdown.
## Inspiration
We first thought of RecipEase because we noticed how many people had dietary restrictions, and wanted a way to create food recipes with those dietary restrictions in mind. We also knew that many college students, like ourselves, either were already living alone in apartments or about to, and have little to no cooking experience. Because of this, RecipEase was brought to life - as a quick, easy-to-use application that can bring new flavors and ideas to your kitchen.

## What it does
RecipEase allows you to level up your meals by providing personalized meal recommendations based on your dietary restrictions, the ingredients you have readily available, and your preferred cuisine and ingredients. It launches you into a login authentication process, where you can signup or login to your account. Then, you can select ingredients, dietary restrictions, and based on that, our program will give multiple recipes to try out. From there, you can even select a recipe to view more detailed information such as cooking instructions as well as nutrition information. 

## How we built it
We used Streamlit as our app framework to handle user authentication and front-end design. Groq’s LLM API was implemented to infer recipes based on a user’s personalized settings and obtain step-by-step instructions for the cooking process. Our project also utilized SQLite to store user data and maintain past query history. We primarily programmed in Python. 

## Challenges we ran into
Our team juggled back and forth between project ideas and what features we could reasonably implement with the time constraints of the contest. We spent a lot of time consolidating all the aspects of our project together (bringing all our individual components together, merging conflicts, etc), but we ultimately honed in on a final vision of the project that functions well. 
 
## Accomplishments that we're proud of

We’re all proud of everything we’ve accomplished these last 25 hours, as this was all of our first hackathons. We’re happy to have a pretty complete product, with reasonably good UI and fully functional features as well. We also learned a lot from some of the workshops, as well as just understanding more about full-stack development throughout this entire process. The learning process is the most important part, so we’re all happy that we were able to grow as programmers.

## What we learned

We learned about using virtual environments such as conda to store environment variables(allowing us to store the API keys separately). Using APIs was another big thing that our project incorporated a lot of, so we got pretty familiar with them. We also learned that despite what seemed like a long time to work, that time quickly became shortened when we ran into roadblocks. For the next hackathon, we’ll be sure to manage our time more efficiently.

## What's next for RecipEase

What’s next is training our image recognition model on more datasets, and running it through more epochs to ensure maximum accuracy. The RecipEase web app could also use some more work on its aesthetics, with a cleaner UI and clear instructions. 

### How to run it on your own machine

1. Install the requirements

   ```
   $ pip install -r requirements.txt
   ```

2. Run the app

   ```
   $ streamlit run streamlit_app.py
   ```
